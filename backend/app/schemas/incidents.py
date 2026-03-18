"""Incident schemas."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class IncidentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    description: str
    severity: str
    category: str
    user_email: Optional[str]
    device_id: Optional[uuid.UUID]
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime]
    source_data: Optional[dict]
    created_at: datetime


class IncidentListResponse(BaseModel):
    items: List[IncidentResponse]
    total: int
    page: int
    page_size: int


class IncidentCreate(BaseModel):
    title: str
    description: str = ""
    severity: str = "low"
    category: str = "other"
    user_email: Optional[str] = None
    device_id: Optional[uuid.UUID] = None
