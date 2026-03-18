"""Security incident endpoints."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_tenant_id
from app.models.incident import Incident
from app.schemas.incidents import IncidentCreate, IncidentListResponse, IncidentResponse

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> IncidentListResponse:
    """Paginated incident list with filtering."""
    tid = uuid.UUID(tenant_id)
    query = select(Incident).where(Incident.tenant_id == tid)

    if severity:
        query = query.where(Incident.severity == severity)
    if status:
        query = query.where(Incident.status == status)
    if category:
        query = query.where(Incident.category == category)

    count_r = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_r.scalar_one() or 0

    query = (
        query.order_by(Incident.detected_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    incidents = result.scalars().all()

    return IncidentListResponse(
        items=[IncidentResponse.model_validate(i) for i in incidents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(
    data: IncidentCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Manually create a security incident."""
    tid = uuid.UUID(tenant_id)
    incident = Incident(
        tenant_id=tid,
        title=data.title,
        description=data.description,
        severity=data.severity,
        category=data.category,
        user_email=data.user_email,
        device_id=data.device_id,
    )
    db.add(incident)
    await db.flush()
    await db.refresh(incident)
    return IncidentResponse.model_validate(incident)


@router.post("/{incident_id}/acknowledge", response_model=IncidentResponse)
async def acknowledge_incident(
    incident_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Move an incident to acknowledged status."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id, Incident.tenant_id == tid)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status == "resolved":
        raise HTTPException(status_code=400, detail="Cannot acknowledge a resolved incident")

    incident.status = "acknowledged"
    await db.flush()
    await db.refresh(incident)
    return IncidentResponse.model_validate(incident)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Mark an incident as resolved."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id, Incident.tenant_id == tid)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = "resolved"
    incident.resolved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(incident)
    return IncidentResponse.model_validate(incident)
