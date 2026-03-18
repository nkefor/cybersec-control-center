"""Remediation task CRUD endpoints."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_tenant_id
from app.models.task import Task
from app.schemas.tasks import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """List remediation tasks with optional filtering."""
    tid = uuid.UUID(tenant_id)
    query = select(Task).where(Task.tenant_id == tid)

    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)

    count_r = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_r.scalar_one() or 0

    query = query.order_by(
        Task.status, Task.priority.desc(), Task.created_at.desc()
    )
    result = await db.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
    )


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Create a new remediation task."""
    tid = uuid.UUID(tenant_id)
    task = Task(
        tenant_id=tid,
        title=data.title,
        description=data.description,
        priority=data.priority,
        assigned_to=data.assigned_to,
        related_incident_id=data.related_incident_id,
        due_date=data.due_date,
        status="todo",
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update a task's status, priority, assignee, or other fields."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.tenant_id == tid)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = data.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(task, field, value)

    # Manage completed_at based on status transitions
    if data.status == "done" and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)
    elif data.status is not None and data.status != "done":
        task.completed_at = None

    await db.flush()
    await db.refresh(task)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a task."""
    tid = uuid.UUID(tenant_id)
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.tenant_id == tid)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
