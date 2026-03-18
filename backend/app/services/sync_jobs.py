"""APScheduler background sync jobs."""

import json
import logging
import uuid
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import String, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.incident import Incident
from app.models.task import Task
from app.models.tenant import Tenant
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler(timezone="UTC")


async def sync_tenant(tenant: Tenant, db: AsyncSession) -> None:
    """Sync one tenant's data from connected identity providers."""
    logger.info("Starting sync for tenant: %s", tenant.name)

    synced_users: list[dict] = []

    # Microsoft 365 sync
    if tenant.microsoft_connected and tenant.microsoft_access_token:
        try:
            from app.services.microsoft_graph import MicrosoftGraphService

            svc = MicrosoftGraphService(tenant.microsoft_access_token)
            ms_users = await svc.get_users_with_mfa()
            synced_users.extend(ms_users)

            # Check for risky sign-ins and create incidents
            risky = await svc.get_risky_sign_ins()
            for signin in risky:
                existing = await db.execute(
                    select(Incident).where(
                        Incident.tenant_id == tenant.id,
                        cast(Incident.source_data["signin_id"], String) == signin.get("id"),
                    )
                )
                if not existing.scalar_one_or_none():
                    incident = Incident(
                        tenant_id=tenant.id,
                        title=f"Risky sign-in detected for {signin.get('userPrincipalName', 'unknown')}",
                        description=f"Risk level: {signin.get('riskLevel')}. Location: {signin.get('location', {}).get('city', 'unknown')}",
                        severity=_map_risk_level(signin.get("riskLevel", "low")),
                        category="risky_login",
                        user_email=signin.get("userPrincipalName"),
                        source_data={"signin_id": signin.get("id"), **signin},
                    )
                    db.add(incident)
        except Exception as exc:
            logger.error("Microsoft sync failed for %s: %s", tenant.name, exc)

    # Google Workspace sync
    if tenant.google_connected and tenant.google_credentials:
        try:
            from app.services.google_admin import GoogleAdminService

            creds = json.loads(tenant.google_credentials)
            svc = GoogleAdminService(creds)
            g_users = await svc.get_users(tenant.google_domain)
            synced_users.extend(g_users)
        except Exception as exc:
            logger.error("Google sync failed for %s: %s", tenant.name, exc)

    # Upsert users
    for user_data in synced_users:
        existing = await db.execute(
            select(User).where(
                User.tenant_id == tenant.id,
                User.email == user_data["email"],
            )
        )
        user = existing.scalar_one_or_none()
        if user:
            user.display_name = user_data["display_name"]
            user.mfa_enabled = user_data["mfa_enabled"]
            user.mfa_methods = user_data["mfa_methods"]
            user.last_sign_in = user_data["last_sign_in"]
            user.is_active = user_data["is_active"]
            user.updated_at = datetime.now(timezone.utc)
        else:
            user = User(
                tenant_id=tenant.id,
                email=user_data["email"],
                display_name=user_data["display_name"],
                mfa_enabled=user_data["mfa_enabled"],
                mfa_methods=user_data["mfa_methods"],
                last_sign_in=user_data["last_sign_in"],
                is_active=user_data["is_active"],
                external_id=user_data.get("external_id"),
                source=user_data.get("source", "microsoft365"),
            )
            db.add(user)

    # Auto-create tasks for critical issues
    await _auto_create_tasks(tenant, db)

    # Update last sync timestamp
    tenant.last_sync_at = datetime.now(timezone.utc)
    await db.commit()
    logger.info("Sync complete for tenant: %s, %d users synced", tenant.name, len(synced_users))


async def _auto_create_tasks(tenant: Tenant, db: AsyncSession) -> None:
    """Create remediation tasks for newly detected critical issues."""
    # Check for users without MFA
    no_mfa = await db.execute(
        select(User).where(
            User.tenant_id == tenant.id,
            User.is_active == True,
            User.mfa_enabled == False,
        )
    )
    no_mfa_users = no_mfa.scalars().all()

    if len(no_mfa_users) > 5:
        # Only create a task if we don't have a recent one
        existing_task = await db.execute(
            select(Task).where(
                Task.tenant_id == tenant.id,
                Task.title.like("Enable MFA for%"),
                Task.status.in_(["todo", "in_progress"]),
            )
        )
        if not existing_task.scalar_one_or_none():
            task = Task(
                tenant_id=tenant.id,
                title=f"Enable MFA for {len(no_mfa_users)} users",
                description=f"MFA is not enabled for {len(no_mfa_users)} active users. Enable MFA to improve security posture.",
                priority="high",
                status="todo",
            )
            db.add(task)


def _map_risk_level(ms_risk: str) -> str:
    mapping = {
        "none": "info",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "hidden": "low",
        "unknownFutureValue": "low",
    }
    return mapping.get(ms_risk, "medium")


async def run_all_tenant_syncs() -> None:
    """Job entry point: sync all tenants that have active integrations."""
    logger.info("Starting scheduled sync for all tenants")
    # Fetch IDs first, then process each tenant in its own isolated session
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Tenant.id).where(
                (Tenant.microsoft_access_token.isnot(None))
                | (Tenant.google_credentials.isnot(None))
            )
        )
        tenant_ids = result.scalars().all()

    for tenant_id in tenant_ids:
        async with AsyncSessionLocal() as db:
            try:
                tenant_result = await db.execute(
                    select(Tenant).where(Tenant.id == tenant_id)
                )
                tenant = tenant_result.scalar_one_or_none()
                if tenant:
                    await sync_tenant(tenant, db)
            except Exception as exc:
                logger.error("Sync failed for tenant %s: %s", tenant_id, exc)
                await db.rollback()


def start_scheduler() -> None:
    """Register jobs and start APScheduler."""
    scheduler.add_job(
        run_all_tenant_syncs,
        "interval",
        minutes=settings.sync_interval_minutes,
        id="tenant_sync",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started. Sync interval: %d minutes", settings.sync_interval_minutes
    )


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
