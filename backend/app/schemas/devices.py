"""Device posture schemas."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DeviceResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    device_name: str
    owner_email: Optional[str]
    os_type: str
    os_version: Optional[str]
    is_compliant: bool
    encryption_enabled: bool
    last_seen: Optional[datetime]
    compliance_issues: Optional[List[str]]
    risk_score: int
    source: str
    created_at: datetime


class DeviceListResponse(BaseModel):
    items: List[DeviceResponse]
    total: int
    page: int
    page_size: int


class DevicePostureSummary(BaseModel):
    total: int
    compliant: int
    noncompliant: int
    compliance_rate: float
    encrypted: int
    encryption_rate: float
    by_os: dict
