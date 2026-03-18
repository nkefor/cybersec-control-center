"""Backup job tracking model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BackupJob(Base):
    __tablename__ = "backup_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_description: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    # Timing
    last_backup_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_backup_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        Enum("healthy", "warning", "critical", "unknown", name="backup_status"),
        nullable=False,
        default="unknown",
    )

    # Metadata
    backup_size_gb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    provider: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
