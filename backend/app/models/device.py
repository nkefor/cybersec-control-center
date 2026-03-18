"""Device posture model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)

    # OS details
    os_type: Mapped[str] = mapped_column(
        Enum("windows", "macos", "linux", "ios", "android", "other", name="os_type"),
        nullable=False,
        default="other",
    )
    os_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Compliance
    is_compliant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    encryption_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    compliance_issues: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Risk scoring 0-100
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    source: Mapped[str] = mapped_column(
        Enum("microsoft365", "google", "manual", name="device_source"),
        nullable=False,
        default="manual",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
