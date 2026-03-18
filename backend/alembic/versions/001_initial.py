"""Initial schema migration.

Revision ID: 001
Revises:
Create Date: 2024-01-15 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # tenants
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "plan",
            sa.Enum("starter", "professional", "msp", name="tenant_plan"),
            nullable=False,
            server_default="starter",
        ),
        sa.Column("microsoft_tenant_id", sa.String(255), nullable=True),
        sa.Column("microsoft_access_token", sa.Text, nullable=True),
        sa.Column("microsoft_refresh_token", sa.Text, nullable=True),
        sa.Column("microsoft_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("google_domain", sa.String(255), nullable=True),
        sa.Column("google_credentials", sa.Text, nullable=True),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("mfa_methods", postgresql.JSON, nullable=True),
        sa.Column("last_sign_in", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("risk_level", sa.Enum("none", "low", "medium", "high", name="risk_level"), nullable=False, server_default="none"),
        sa.Column("source", sa.Enum("microsoft365", "google", "manual", name="user_source"), nullable=False, server_default="manual"),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # devices
    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_name", sa.String(255), nullable=False),
        sa.Column("owner_email", sa.String(320), nullable=True),
        sa.Column("os_type", sa.Enum("windows", "macos", "linux", "ios", "android", "other", name="os_type"), nullable=False, server_default="other"),
        sa.Column("os_version", sa.String(100), nullable=True),
        sa.Column("is_compliant", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("encryption_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("compliance_issues", postgresql.JSON, nullable=True),
        sa.Column("risk_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("source", sa.Enum("microsoft365", "google", "manual", name="device_source"), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_devices_tenant_id", "devices", ["tenant_id"])

    # backup_jobs
    op.create_table(
        "backup_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("target_description", sa.String(500), nullable=False, server_default=""),
        sa.Column("last_backup_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_backup_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Enum("healthy", "warning", "critical", "unknown", name="backup_status"), nullable=False, server_default="unknown"),
        sa.Column("backup_size_gb", sa.Float, nullable=True),
        sa.Column("retention_days", sa.Integer, nullable=False, server_default="30"),
        sa.Column("provider", sa.String(100), nullable=False, server_default="manual"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_backup_jobs_tenant_id", "backup_jobs", ["tenant_id"])

    # incidents
    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("severity", sa.Enum("info", "low", "medium", "high", "critical", name="incident_severity"), nullable=False, server_default="low"),
        sa.Column("category", sa.Enum("risky_login", "mfa_bypass", "inactive_account", "device_noncompliance", "backup_failure", "phishing", "other", name="incident_category"), nullable=False, server_default="other"),
        sa.Column("user_email", sa.String(320), nullable=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.Enum("open", "acknowledged", "resolved", name="incident_status"), nullable=False, server_default="open"),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_data", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_incidents_tenant_id", "incidents", ["tenant_id"])

    # tasks
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("priority", sa.Enum("low", "medium", "high", "critical", name="task_priority"), nullable=False, server_default="medium"),
        sa.Column("status", sa.Enum("todo", "in_progress", "done", "dismissed", name="task_status"), nullable=False, server_default="todo"),
        sa.Column("assigned_to", sa.String(320), nullable=True),
        sa.Column("related_incident_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tasks_tenant_id", "tasks", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_table("incidents")
    op.drop_table("backup_jobs")
    op.drop_table("devices")
    op.drop_table("users")
    op.drop_table("tenants")
    for enum in ["tenant_plan", "risk_level", "user_source", "os_type", "device_source",
                 "backup_status", "incident_severity", "incident_category", "incident_status",
                 "task_priority", "task_status"]:
        sa.Enum(name=enum).drop(op.get_bind(), checkfirst=True)
