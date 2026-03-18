"""Task schemas."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TaskResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    description: Optional[str]
    priority: str
    status: str
    assigned_to: Optional[str]
    related_incident_id: Optional[uuid.UUID]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assigned_to: Optional[str] = None
    related_incident_id: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
