"""Dashboard summary endpoint."""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import DEMO_TENANT_ID, get_current_tenant_id
from app.models.backup import BackupJob
from app.models.device import Device
from app.models.incident import Incident
from app.models.task import Task
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.dashboard import BackupSummary, DashboardSummary, DeviceSummary, MFACoverage
from app.services.security_score import calculate_security_score

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    """Return the aggregate security dashboard summary for the current tenant."""
    tid = uuid.UUID(tenant_id)

    # Tenant info
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == tid))
    tenant = tenant_result.scalar_one_or_none()
    tenant_name = tenant.name if tenant else "Your Organization"
    last_synced = tenant.last_sync_at if tenant else None

    # MFA coverage
    total_users_r = await db.execute(
        select(func.count()).where(User.tenant_id == tid, User.is_active == True)
    )
    total_users = total_users_r.scalar_one() or 0

    mfa_users_r = await db.execute(
        select(func.count()).where(
            User.tenant_id == tid, User.is_active == True, User.mfa_enabled == True
        )
    )
    mfa_users = mfa_users_r.scalar_one() or 0
    mfa_pct = round((mfa_users / total_users * 100) if total_users > 0 else 0, 1)

    # Risky logins in last 24 hours
    cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    risky_r = await db.execute(
        select(func.count()).where(
            Incident.tenant_id == tid,
            Incident.category == "risky_login",
            Incident.detected_at >= cutoff_24h,
        )
    )
    risky_logins = risky_r.scalar_one() or 0

    # Device posture
    total_devices_r = await db.execute(
        select(func.count()).where(Device.tenant_id == tid)
    )
    total_devices = total_devices_r.scalar_one() or 0

    compliant_r = await db.execute(
        select(func.count()).where(Device.tenant_id == tid, Device.is_compliant == True)
    )
    compliant = compliant_r.scalar_one() or 0

    # Backup health
    backup_counts: dict[str, int] = {}
    for status_val in ["healthy", "warning", "critical", "unknown"]:
        r = await db.execute(
            select(func.count()).where(
                BackupJob.tenant_id == tid, BackupJob.status == status_val
            )
        )
        backup_counts[status_val] = r.scalar_one() or 0

    # Tasks
    open_tasks_r = await db.execute(
        select(func.count()).where(
            Task.tenant_id == tid, Task.status.in_(["todo", "in_progress"])
        )
    )
    open_tasks = open_tasks_r.scalar_one() or 0

    # Critical open incidents
    critical_r = await db.execute(
        select(func.count()).where(
            Incident.tenant_id == tid,
            Incident.status == "open",
            Incident.severity.in_(["critical", "high"]),
        )
    )
    critical_incidents = critical_r.scalar_one() or 0

    # Security score
    security_score = await calculate_security_score(db, tid)

    return DashboardSummary(
        security_score=security_score,
        score_change_7d=5,  # Would compare to 7-day-ago snapshot in production
        mfa_coverage=MFACoverage(
            enabled=mfa_users,
            total=total_users,
            percentage=mfa_pct,
        ),
        risky_logins_24h=risky_logins,
        devices=DeviceSummary(
            compliant=compliant,
            noncompliant=total_devices - compliant,
            total=total_devices,
        ),
        backups=BackupSummary(
            healthy=backup_counts["healthy"],
            warning=backup_counts["warning"],
            critical=backup_counts["critical"],
            unknown=backup_counts["unknown"],
        ),
        open_tasks=open_tasks,
        critical_incidents=critical_incidents,
        last_synced=last_synced,
        tenant_name=tenant_name,
    )
