"""Backup status endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_tenant_id
from app.models.backup import BackupJob
from app.schemas.backups import (
    BackupCreate,
    BackupJobResponse,
    BackupListResponse,
    BackupUpdate,
)

router = APIRouter(prefix="/api/backups", tags=["backups"])


@router.get("", response_model=BackupListResponse)
async def list_backups(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> BackupListResponse:
    """List all backup jobs and their current status."""
    tid = uuid.UUID(tenant_id)
    query = select(BackupJob).where(BackupJob.tenant_id == tid)

    if status:
        query = query.where(BackupJob.status == status)

    query = query.order_by(BackupJob.name)
    result = await db.execute(query)
    jobs = result.scalars().all()

    return BackupListResponse(
        items=[BackupJobResponse.model_validate(j) for j in jobs],
        total=len(jobs),
    )


@router.post("", response_model=BackupJobResponse, status_code=201)
async def create_backup(
    data: BackupCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> BackupJobResponse:
    """Register a new backup job for tracking."""
    tid = uuid.UUID(tenant_id)
    job = BackupJob(
        tenant_id=tid,
        name=data.name,
        target_description=data.target_description,
        provider=data.provider,
        retention_days=data.retention_days,
        notes=data.notes,
        status="unknown",
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return BackupJobResponse.model_validate(job)


@router.patch("/{backup_id}", response_model=BackupJobResponse)
async def update_backup(
    backup_id: uuid.UUID,
    data: BackupUpdate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> BackupJobResponse:
    """Update backup job status or metadata."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(
        select(BackupJob).where(BackupJob.id == backup_id, BackupJob.tenant_id == tid)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Backup job not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(job, field, value)

    await db.flush()
    await db.refresh(job)
    return BackupJobResponse.model_validate(job)


@router.delete("/{backup_id}", status_code=204)
async def delete_backup(
    backup_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a backup job from tracking."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(
        select(BackupJob).where(BackupJob.id == backup_id, BackupJob.tenant_id == tid)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Backup job not found")
    await db.delete(job)
