"""Tenant / organization model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    plan: Mapped[str] = mapped_column(
        Enum("starter", "professional", "msp", name="tenant_plan"),
        nullable=False,
        default="starter",
    )

    # Microsoft 365 integration
    microsoft_tenant_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    microsoft_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    microsoft_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    microsoft_token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Google Workspace integration
    google_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    google_credentials: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Sync tracking
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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

    @property
    def microsoft_connected(self) -> bool:
        return bool(self.microsoft_access_token and self.microsoft_tenant_id)

    @property
    def google_connected(self) -> bool:
        return bool(self.google_credentials and self.google_domain)
