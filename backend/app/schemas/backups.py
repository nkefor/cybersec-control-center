"""Backup job schemas."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BackupJobResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    target_description: str
    last_backup_at: Optional[datetime]
    next_backup_at: Optional[datetime]
    status: str
    backup_size_gb: Optional[float]
    retention_days: int
    provider: str
    notes: Optional[str]
    created_at: datetime


class BackupListResponse(BaseModel):
    items: List[BackupJobResponse]
    total: int


class BackupCreate(BaseModel):
    name: str
    target_description: str
    provider: str = "manual"
    retention_days: int = 30
    notes: Optional[str] = None


class BackupUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    last_backup_at: Optional[datetime] = None
    next_backup_at: Optional[datetime] = None
    backup_size_gb: Optional[float] = None
    notes: Optional[str] = None
