"""Dashboard summary schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MFACoverage(BaseModel):
    enabled: int
    total: int
    percentage: float


class DeviceSummary(BaseModel):
    compliant: int
    noncompliant: int
    total: int


class BackupSummary(BaseModel):
    healthy: int
    warning: int
    critical: int
    unknown: int


class DashboardSummary(BaseModel):
    security_score: int
    score_change_7d: int
    mfa_coverage: MFACoverage
    risky_logins_24h: int
    devices: DeviceSummary
    backups: BackupSummary
    open_tasks: int
    critical_incidents: int
    last_synced: Optional[datetime]
    tenant_name: str
