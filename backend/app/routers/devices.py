"""Device posture endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_tenant_id
from app.models.device import Device
from app.schemas.devices import DeviceListResponse, DevicePostureSummary, DeviceResponse

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("", response_model=DeviceListResponse)
async def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    is_compliant: Optional[bool] = Query(None),
    os_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> DeviceListResponse:
    """Paginated device list with posture details."""
    tid = uuid.UUID(tenant_id)
    query = select(Device).where(Device.tenant_id == tid)

    if is_compliant is not None:
        query = query.where(Device.is_compliant == is_compliant)
    if os_type:
        query = query.where(Device.os_type == os_type)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (Device.device_name.ilike(pattern)) | (Device.owner_email.ilike(pattern))
        )

    count_r = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_r.scalar_one() or 0

    query = (
        query.order_by(Device.risk_score.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    devices = result.scalars().all()

    return DeviceListResponse(
        items=[DeviceResponse.model_validate(d) for d in devices],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/posture-summary", response_model=DevicePostureSummary)
async def get_posture_summary(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> DevicePostureSummary:
    """Aggregate device posture statistics."""
    tid = uuid.UUID(tenant_id)

    total_r = await db.execute(select(func.count()).where(Device.tenant_id == tid))
    total = total_r.scalar_one() or 0

    compliant_r = await db.execute(
        select(func.count()).where(Device.tenant_id == tid, Device.is_compliant == True)
    )
    compliant = compliant_r.scalar_one() or 0

    encrypted_r = await db.execute(
        select(func.count()).where(
            Device.tenant_id == tid, Device.encryption_enabled == True
        )
    )
    encrypted = encrypted_r.scalar_one() or 0

    # OS breakdown
    os_r = await db.execute(
        select(Device.os_type, func.count().label("count"))
        .where(Device.tenant_id == tid)
        .group_by(Device.os_type)
    )
    by_os = {row.os_type: row.count for row in os_r}

    return DevicePostureSummary(
        total=total,
        compliant=compliant,
        noncompliant=total - compliant,
        compliance_rate=round((compliant / total * 100) if total > 0 else 0, 1),
        encrypted=encrypted,
        encryption_rate=round((encrypted / total * 100) if total > 0 else 0, 1),
        by_os=by_os,
    )
