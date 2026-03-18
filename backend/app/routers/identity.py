"""Identity and user management endpoints."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_tenant_id
from app.models.user import User
from app.schemas.identity import (
    InactiveUserResponse,
    MFASummary,
    UserListResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/identity", tags=["identity"])


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    mfa_enabled: Optional[bool] = Query(None),
    risk_level: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None, alias="active"),
    search: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> UserListResponse:
    """Paginated user list with optional filtering."""
    tid = uuid.UUID(tenant_id)
    query = select(User).where(User.tenant_id == tid)

    if mfa_enabled is not None:
        query = query.where(User.mfa_enabled == mfa_enabled)
    if risk_level:
        query = query.where(User.risk_level == risk_level)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (User.email.ilike(pattern)) | (User.display_name.ilike(pattern))
        )

    count_r = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_r.scalar_one() or 0

    query = query.order_by(User.display_name).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/mfa-summary", response_model=MFASummary)
async def get_mfa_summary(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> MFASummary:
    """MFA coverage breakdown across the organization."""
    tid = uuid.UUID(tenant_id)

    total_r = await db.execute(
        select(func.count()).where(User.tenant_id == tid, User.is_active == True)
    )
    total = total_r.scalar_one() or 0

    enabled_r = await db.execute(
        select(func.count()).where(
            User.tenant_id == tid, User.is_active == True, User.mfa_enabled == True
        )
    )
    enabled = enabled_r.scalar_one() or 0
    disabled = total - enabled

    coverage = round((enabled / total * 100) if total > 0 else 0, 1)

    # Method breakdown — query all users with MFA for method analysis
    mfa_users_r = await db.execute(
        select(User.mfa_methods).where(
            User.tenant_id == tid,
            User.is_active == True,
            User.mfa_enabled == True,
            User.mfa_methods.isnot(None),
        )
    )
    methods_breakdown: dict[str, int] = {}
    for (methods,) in mfa_users_r:
        if methods:
            for method in methods:
                methods_breakdown[method] = methods_breakdown.get(method, 0) + 1

    return MFASummary(
        total_users=total,
        mfa_enabled=enabled,
        mfa_disabled=disabled,
        coverage_percentage=coverage,
        methods_breakdown=methods_breakdown,
    )


@router.get("/inactive-users", response_model=list[InactiveUserResponse])
async def get_inactive_users(
    days: int = Query(30, ge=1, le=365),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[InactiveUserResponse]:
    """Return users who have not signed in within the specified number of days."""
    tid = uuid.UUID(tenant_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(User)
        .where(
            User.tenant_id == tid,
            User.is_active == True,
            User.last_sign_in < cutoff,
        )
        .order_by(User.last_sign_in)
    )
    users = result.scalars().all()
    now = datetime.now(timezone.utc)

    return [
        InactiveUserResponse(
            id=u.id,
            email=u.email,
            display_name=u.display_name,
            last_sign_in=u.last_sign_in,
            days_inactive=(now - u.last_sign_in).days if u.last_sign_in else days,
            risk_level=u.risk_level,
        )
        for u in users
    ]


@router.post("/sync")
async def trigger_sync(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Trigger a manual sync of identity data from connected providers."""
    from app.models.tenant import Tenant
    from app.services.sync_jobs import sync_tenant

    tid = uuid.UUID(tenant_id)
    tenant_r = await db.execute(select(Tenant).where(Tenant.id == tid))
    tenant = tenant_r.scalar_one_or_none()

    if not tenant:
        return {"status": "error", "message": "Tenant not found"}

    if not (tenant.microsoft_connected or tenant.google_connected):
        return {
            "status": "skipped",
            "message": "No identity providers connected. Configure integrations first.",
        }

    try:
        await sync_tenant(tenant, db)
        return {"status": "success", "message": "Sync completed successfully"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
