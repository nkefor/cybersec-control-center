"""Security incident model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Classification
    severity: Mapped[str] = mapped_column(
        Enum("info", "low", "medium", "high", "critical", name="incident_severity"),
        nullable=False,
        default="low",
    )
    category: Mapped[str] = mapped_column(
        Enum(
            "risky_login",
            "mfa_bypass",
            "inactive_account",
            "device_noncompliance",
            "backup_failure",
            "phishing",
            "other",
            name="incident_category",
        ),
        nullable=False,
        default="other",
    )

    # Context
    user_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )

    # Lifecycle
    status: Mapped[str] = mapped_column(
        Enum("open", "acknowledged", "resolved", name="incident_status"),
        nullable=False,
        default="open",
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Raw data from source
    source_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
