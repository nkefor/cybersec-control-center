"""Identity / user schemas."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    display_name: str
    mfa_enabled: bool
    mfa_methods: Optional[List[str]]
    last_sign_in: Optional[datetime]
    is_active: bool
    risk_level: str
    source: str
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    page_size: int


class MFASummary(BaseModel):
    total_users: int
    mfa_enabled: int
    mfa_disabled: int
    coverage_percentage: float
    methods_breakdown: dict


class InactiveUserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    display_name: str
    last_sign_in: Optional[datetime]
    days_inactive: int
    risk_level: str
