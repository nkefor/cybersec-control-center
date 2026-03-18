"""Security score calculator — weighted scoring across all control domains."""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup import BackupJob
from app.models.device import Device
from app.models.incident import Incident
from app.models.user import User


async def calculate_security_score(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """
    Weighted security score (0-100):
      MFA coverage          30 pts
      No critical incidents 25 pts
      Device compliance     20 pts
      Backup health         15 pts
      No inactive users     10 pts
    """
    score = 0

    # --- MFA coverage (30 pts) ---
    total_users_result = await db.execute(
        select(func.count()).where(User.tenant_id == tenant_id, User.is_active == True)
    )
    total_users = total_users_result.scalar_one() or 0

    mfa_users_result = await db.execute(
        select(func.count()).where(
            User.tenant_id == tenant_id,
            User.is_active == True,
            User.mfa_enabled == True,
        )
    )
    mfa_users = mfa_users_result.scalar_one() or 0

    if total_users > 0:
        mfa_rate = mfa_users / total_users
        score += round(mfa_rate * 30)

    # --- No critical/high open incidents (25 pts) ---
    critical_incidents_result = await db.execute(
        select(func.count()).where(
            Incident.tenant_id == tenant_id,
            Incident.status == "open",
            Incident.severity.in_(["critical", "high"]),
        )
    )
    critical_count = critical_incidents_result.scalar_one() or 0

    if critical_count == 0:
        score += 25
    elif critical_count <= 2:
        score += 15
    elif critical_count <= 5:
        score += 5

    # --- Device compliance (20 pts) ---
    total_devices_result = await db.execute(
        select(func.count()).where(Device.tenant_id == tenant_id)
    )
    total_devices = total_devices_result.scalar_one() or 0

    compliant_result = await db.execute(
        select(func.count()).where(
            Device.tenant_id == tenant_id, Device.is_compliant == True
        )
    )
    compliant = compliant_result.scalar_one() or 0

    if total_devices > 0:
        compliance_rate = compliant / total_devices
        score += round(compliance_rate * 20)

    # --- Backup health (15 pts) ---
    total_backups_result = await db.execute(
        select(func.count()).where(BackupJob.tenant_id == tenant_id)
    )
    total_backups = total_backups_result.scalar_one() or 0

    healthy_backups_result = await db.execute(
        select(func.count()).where(
            BackupJob.tenant_id == tenant_id, BackupJob.status == "healthy"
        )
    )
    healthy_backups = healthy_backups_result.scalar_one() or 0

    if total_backups > 0:
        backup_rate = healthy_backups / total_backups
        score += round(backup_rate * 15)
    elif total_backups == 0:
        # No backups configured is concerning
        score += 0

    # --- No inactive users (10 pts) ---
    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    inactive_result = await db.execute(
        select(func.count()).where(
            User.tenant_id == tenant_id,
            User.is_active == True,
            # Include never-signed-in accounts (NULL last_sign_in) as inactive
            (User.last_sign_in < cutoff) | (User.last_sign_in.is_(None)),
        )
    )
    inactive = inactive_result.scalar_one() or 0

    if total_users > 0:
        inactive_rate = inactive / total_users
        if inactive_rate < 0.05:
            score += 10
        elif inactive_rate < 0.10:
            score += 7
        elif inactive_rate < 0.20:
            score += 3

    return min(max(score, 0), 100)
