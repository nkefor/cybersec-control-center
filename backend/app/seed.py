"""
Demo data seeder for development.

Creates a complete dataset for "Acme Law Firm":
  - 50 users (45 with MFA, 5 inactive)
  - 55 devices (48 compliant, 7 non-compliant)
  - 9 backup jobs (8 healthy, 1 warning)
  - 3 risky login incidents + additional incidents
  - 12 open tasks
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.middleware.auth import DEMO_TENANT_ID
from app.models.backup import BackupJob
from app.models.device import Device
from app.models.incident import Incident
from app.models.task import Task
from app.models.tenant import Tenant
from app.models.user import User

logger = logging.getLogger(__name__)

now = datetime.now(timezone.utc)
TENANT_ID = uuid.UUID(DEMO_TENANT_ID)


def _days_ago(days: int) -> datetime:
    return now - timedelta(days=days)


def _hours_ago(hours: int) -> datetime:
    return now - timedelta(hours=hours)


USERS_DATA = [
    # Active users with MFA (45 total)
    {"email": "sarah.chen@acmelawfirm.com", "display_name": "Sarah Chen", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "phoneCall"], "last_sign_in": _hours_ago(2), "risk_level": "none"},
    {"email": "michael.torres@acmelawfirm.com", "display_name": "Michael Torres", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(5), "risk_level": "none"},
    {"email": "jennifer.walsh@acmelawfirm.com", "display_name": "Jennifer Walsh", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "sms"], "last_sign_in": _days_ago(1), "risk_level": "none"},
    {"email": "david.kim@acmelawfirm.com", "display_name": "David Kim", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(1), "risk_level": "none"},
    {"email": "lisa.patel@acmelawfirm.com", "display_name": "Lisa Patel", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(8), "risk_level": "none"},
    {"email": "james.anderson@acmelawfirm.com", "display_name": "James Anderson", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "email"], "last_sign_in": _days_ago(2), "risk_level": "low"},
    {"email": "emily.rodriguez@acmelawfirm.com", "display_name": "Emily Rodriguez", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(3), "risk_level": "none"},
    {"email": "robert.johnson@acmelawfirm.com", "display_name": "Robert Johnson", "mfa_enabled": True, "mfa_methods": ["phoneCall"], "last_sign_in": _days_ago(3), "risk_level": "none"},
    {"email": "amanda.white@acmelawfirm.com", "display_name": "Amanda White", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(12), "risk_level": "none"},
    {"email": "christopher.lee@acmelawfirm.com", "display_name": "Christopher Lee", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "sms"], "last_sign_in": _days_ago(1), "risk_level": "none"},
    {"email": "michelle.garcia@acmelawfirm.com", "display_name": "Michelle Garcia", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(2), "risk_level": "none"},
    {"email": "kevin.martinez@acmelawfirm.com", "display_name": "Kevin Martinez", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(6), "risk_level": "none"},
    {"email": "patricia.thompson@acmelawfirm.com", "display_name": "Patricia Thompson", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(4), "risk_level": "none"},
    {"email": "andrew.harris@acmelawfirm.com", "display_name": "Andrew Harris", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(18), "risk_level": "none"},
    {"email": "stephanie.clark@acmelawfirm.com", "display_name": "Stephanie Clark", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "email"], "last_sign_in": _days_ago(5), "risk_level": "none"},
    {"email": "matthew.lewis@acmelawfirm.com", "display_name": "Matthew Lewis", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(1), "risk_level": "none"},
    {"email": "jessica.robinson@acmelawfirm.com", "display_name": "Jessica Robinson", "mfa_enabled": True, "mfa_methods": ["sms"], "last_sign_in": _hours_ago(7), "risk_level": "none"},
    {"email": "daniel.walker@acmelawfirm.com", "display_name": "Daniel Walker", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(3), "risk_level": "none"},
    {"email": "nicole.hall@acmelawfirm.com", "display_name": "Nicole Hall", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(2), "risk_level": "none"},
    {"email": "ryan.allen@acmelawfirm.com", "display_name": "Ryan Allen", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "phoneCall"], "last_sign_in": _hours_ago(4), "risk_level": "none"},
    {"email": "heather.young@acmelawfirm.com", "display_name": "Heather Young", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(6), "risk_level": "none"},
    {"email": "brandon.hernandez@acmelawfirm.com", "display_name": "Brandon Hernandez", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(9), "risk_level": "none"},
    {"email": "megan.king@acmelawfirm.com", "display_name": "Megan King", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "sms"], "last_sign_in": _days_ago(1), "risk_level": "none"},
    {"email": "tyler.wright@acmelawfirm.com", "display_name": "Tyler Wright", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(15), "risk_level": "none"},
    {"email": "rachel.scott@acmelawfirm.com", "display_name": "Rachel Scott", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(4), "risk_level": "none"},
    {"email": "joshua.green@acmelawfirm.com", "display_name": "Joshua Green", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(20), "risk_level": "none"},
    {"email": "brittany.adams@acmelawfirm.com", "display_name": "Brittany Adams", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "email"], "last_sign_in": _days_ago(7), "risk_level": "none"},
    {"email": "eric.baker@acmelawfirm.com", "display_name": "Eric Baker", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(2), "risk_level": "none"},
    {"email": "crystal.gonzalez@acmelawfirm.com", "display_name": "Crystal Gonzalez", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(11), "risk_level": "none"},
    {"email": "sean.nelson@acmelawfirm.com", "display_name": "Sean Nelson", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "phoneCall"], "last_sign_in": _days_ago(3), "risk_level": "none"},
    {"email": "ashley.carter@acmelawfirm.com", "display_name": "Ashley Carter", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(6), "risk_level": "none"},
    {"email": "zachary.mitchell@acmelawfirm.com", "display_name": "Zachary Mitchell", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(5), "risk_level": "none"},
    {"email": "brittney.perez@acmelawfirm.com", "display_name": "Brittney Perez", "mfa_enabled": True, "mfa_methods": ["sms"], "last_sign_in": _days_ago(1), "risk_level": "none"},
    {"email": "cody.roberts@acmelawfirm.com", "display_name": "Cody Roberts", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(3), "risk_level": "none"},
    {"email": "kayla.turner@acmelawfirm.com", "display_name": "Kayla Turner", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "email"], "last_sign_in": _days_ago(2), "risk_level": "none"},
    {"email": "austin.phillips@acmelawfirm.com", "display_name": "Austin Phillips", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(14), "risk_level": "none"},
    {"email": "tiffany.campbell@acmelawfirm.com", "display_name": "Tiffany Campbell", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(6), "risk_level": "none"},
    {"email": "aaron.parker@acmelawfirm.com", "display_name": "Aaron Parker", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "sms"], "last_sign_in": _hours_ago(8), "risk_level": "none"},
    {"email": "vanessa.evans@acmelawfirm.com", "display_name": "Vanessa Evans", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(1), "risk_level": "none"},
    {"email": "derek.edwards@acmelawfirm.com", "display_name": "Derek Edwards", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(16), "risk_level": "none"},
    {"email": "tamara.collins@acmelawfirm.com", "display_name": "Tamara Collins", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "phoneCall"], "last_sign_in": _days_ago(4), "risk_level": "none"},
    {"email": "jared.stewart@acmelawfirm.com", "display_name": "Jared Stewart", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(5), "risk_level": "none"},
    {"email": "veronica.sanchez@acmelawfirm.com", "display_name": "Veronica Sanchez", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(3), "risk_level": "none"},
    {"email": "troy.morris@acmelawfirm.com", "display_name": "Troy Morris", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _hours_ago(22), "risk_level": "none"},
    {"email": "diana.rogers@acmelawfirm.com", "display_name": "Diana Rogers", "mfa_enabled": True, "mfa_methods": ["authenticatorApp", "sms"], "last_sign_in": _days_ago(2), "risk_level": "none"},
    # Users WITHOUT MFA (5 users — risky)
    {"email": "frank.butler@acmelawfirm.com", "display_name": "Frank Butler", "mfa_enabled": False, "mfa_methods": [], "last_sign_in": _days_ago(2), "risk_level": "medium"},
    {"email": "linda.simmons@acmelawfirm.com", "display_name": "Linda Simmons", "mfa_enabled": False, "mfa_methods": [], "last_sign_in": _hours_ago(10), "risk_level": "high"},
    {"email": "paul.foster@acmelawfirm.com", "display_name": "Paul Foster", "mfa_enabled": False, "mfa_methods": [], "last_sign_in": _days_ago(5), "risk_level": "medium"},
    {"email": "donna.cox@acmelawfirm.com", "display_name": "Donna Cox", "mfa_enabled": False, "mfa_methods": [], "last_sign_in": _days_ago(1), "risk_level": "medium"},
    {"email": "raymond.ward@acmelawfirm.com", "display_name": "Raymond Ward", "mfa_enabled": False, "mfa_methods": [], "last_sign_in": _days_ago(3), "risk_level": "medium"},
    # Inactive users (5 users — not seen in 30+ days)
    {"email": "carol.price@acmelawfirm.com", "display_name": "Carol Price", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(45), "risk_level": "low"},
    {"email": "henry.james@acmelawfirm.com", "display_name": "Henry James", "mfa_enabled": False, "mfa_methods": [], "last_sign_in": _days_ago(62), "risk_level": "medium"},
    {"email": "sylvia.wood@acmelawfirm.com", "display_name": "Sylvia Wood", "mfa_enabled": True, "mfa_methods": ["authenticatorApp"], "last_sign_in": _days_ago(38), "risk_level": "low"},
    {"email": "oscar.barnes@acmelawfirm.com", "display_name": "Oscar Barnes", "mfa_enabled": False, "mfa_methods": [], "last_sign_in": _days_ago(90), "risk_level": "high"},
    {"email": "grace.ross@acmelawfirm.com", "display_name": "Grace Ross", "mfa_enabled": True, "mfa_methods": ["sms"], "last_sign_in": _days_ago(55), "risk_level": "low"},
]

DEVICES_DATA = [
    # Compliant devices (48)
    *[
        {"device_name": f"ACME-WIN-{i:03d}", "owner_email": USERS_DATA[i % 45]["email"],
         "os_type": "windows", "os_version": "11 22H2", "is_compliant": True,
         "encryption_enabled": True, "last_seen": _hours_ago(i % 48 + 1),
         "compliance_issues": [], "risk_score": 5 + (i % 10)}
        for i in range(30)
    ],
    *[
        {"device_name": f"ACME-MAC-{i:03d}", "owner_email": USERS_DATA[i % 45]["email"],
         "os_type": "macos", "os_version": "14.2", "is_compliant": True,
         "encryption_enabled": True, "last_seen": _hours_ago(i % 72 + 1),
         "compliance_issues": [], "risk_score": 8 + (i % 8)}
        for i in range(18)
    ],
    # Non-compliant devices (7)
    {"device_name": "ACME-WIN-099", "owner_email": "frank.butler@acmelawfirm.com",
     "os_type": "windows", "os_version": "10 21H1", "is_compliant": False,
     "encryption_enabled": False, "last_seen": _days_ago(3),
     "compliance_issues": ["BitLocker not enabled", "OS out of date", "Antivirus disabled"],
     "risk_score": 85},
    {"device_name": "ACME-WIN-101", "owner_email": "linda.simmons@acmelawfirm.com",
     "os_type": "windows", "os_version": "10 20H2", "is_compliant": False,
     "encryption_enabled": True, "last_seen": _days_ago(1),
     "compliance_issues": ["OS out of date", "Missing critical patches"],
     "risk_score": 72},
    {"device_name": "ACME-MAC-088", "owner_email": "paul.foster@acmelawfirm.com",
     "os_type": "macos", "os_version": "12.7", "is_compliant": False,
     "encryption_enabled": False, "last_seen": _days_ago(7),
     "compliance_issues": ["FileVault not enabled", "OS out of date"],
     "risk_score": 68},
    {"device_name": "PERSONAL-WIN-001", "owner_email": "raymond.ward@acmelawfirm.com",
     "os_type": "windows", "os_version": "10 19H1", "is_compliant": False,
     "encryption_enabled": False, "last_seen": _days_ago(2),
     "compliance_issues": ["Unmanaged device", "No encryption", "Very old OS version"],
     "risk_score": 92},
    {"device_name": "ACME-WIN-102", "owner_email": "donna.cox@acmelawfirm.com",
     "os_type": "windows", "os_version": "11 21H2", "is_compliant": False,
     "encryption_enabled": True, "last_seen": _hours_ago(6),
     "compliance_issues": ["Missing required software", "Firewall disabled"],
     "risk_score": 55},
    {"device_name": "ACME-LINUX-001", "owner_email": "carol.price@acmelawfirm.com",
     "os_type": "linux", "os_version": "Ubuntu 20.04", "is_compliant": False,
     "encryption_enabled": True, "last_seen": _days_ago(45),
     "compliance_issues": ["Device not checked in", "Policy compliance unknown"],
     "risk_score": 60},
    {"device_name": "ACME-MAC-092", "owner_email": "oscar.barnes@acmelawfirm.com",
     "os_type": "macos", "os_version": "13.1", "is_compliant": False,
     "encryption_enabled": False, "last_seen": _days_ago(90),
     "compliance_issues": ["Device inactive 90+ days", "FileVault not enabled"],
     "risk_score": 78},
]

BACKUP_JOBS_DATA = [
    {"name": "Client Files - SharePoint", "target_description": "All client case files and documents in SharePoint Online", "status": "healthy", "backup_size_gb": 245.8, "retention_days": 90, "provider": "Veeam", "last_backup_at": _hours_ago(4), "next_backup_at": now + timedelta(hours=20)},
    {"name": "SQL Server - Case Management DB", "target_description": "Primary case management database server", "status": "healthy", "backup_size_gb": 82.3, "retention_days": 365, "provider": "Azure Backup", "last_backup_at": _hours_ago(6), "next_backup_at": now + timedelta(hours=18)},
    {"name": "Email Archive - Exchange Online", "target_description": "All staff email mailboxes and shared mailboxes", "status": "healthy", "backup_size_gb": 189.5, "retention_days": 2555, "provider": "Mimecast", "last_backup_at": _hours_ago(2), "next_backup_at": now + timedelta(hours=22)},
    {"name": "Accounting Files - QuickBooks", "target_description": "QuickBooks company files and financial records", "status": "healthy", "backup_size_gb": 28.7, "retention_days": 2555, "provider": "CrashPlan", "last_backup_at": _hours_ago(8), "next_backup_at": now + timedelta(hours=16)},
    {"name": "HR Documents - OneDrive", "target_description": "Human resources documents, contracts, and personnel files", "status": "healthy", "backup_size_gb": 45.2, "retention_days": 2555, "provider": "Veeam", "last_backup_at": _hours_ago(5), "next_backup_at": now + timedelta(hours=19)},
    {"name": "Network Shares - File Server", "target_description": "On-premises file server shared drives", "status": "healthy", "backup_size_gb": 1240.0, "retention_days": 90, "provider": "Veeam", "last_backup_at": _hours_ago(3), "next_backup_at": now + timedelta(hours=21)},
    {"name": "Virtual Machines - Hyper-V", "target_description": "All on-premises virtual machines and servers", "status": "healthy", "backup_size_gb": 3200.0, "retention_days": 30, "provider": "Veeam", "last_backup_at": _hours_ago(7), "next_backup_at": now + timedelta(hours=17)},
    {"name": "Client Portal Database", "target_description": "Client self-service portal backend database", "status": "healthy", "backup_size_gb": 15.4, "retention_days": 30, "provider": "AWS Backup", "last_backup_at": _hours_ago(1), "next_backup_at": now + timedelta(hours=23)},
    # Warning backup
    {"name": "Physical Records Scan Archive", "target_description": "Scanned physical documents and historical archives", "status": "warning", "backup_size_gb": 892.1, "retention_days": 90, "provider": "NAS Local", "last_backup_at": _days_ago(4), "next_backup_at": _days_ago(1), "notes": "Backup job missed schedule. NAS device showing disk space warnings. Review immediately."},
]

INCIDENTS_DATA = [
    # Risky logins (high severity)
    {"title": "Impossible travel detected — Oscar Barnes", "description": "User Oscar Barnes signed in from New York, NY at 9:14 AM and then from Lagos, Nigeria at 10:52 AM (98 minutes later). Physical travel is impossible. Account may be compromised.", "severity": "high", "category": "risky_login", "user_email": "oscar.barnes@acmelawfirm.com", "status": "open", "detected_at": _hours_ago(3)},
    # Risky logins (medium severity)
    {"title": "Suspicious sign-in from anonymous IP — Linda Simmons", "description": "User Linda Simmons authenticated from a Tor exit node (IP: 185.220.101.x). This IP is flagged as high-risk by Microsoft Threat Intelligence.", "severity": "medium", "category": "risky_login", "user_email": "linda.simmons@acmelawfirm.com", "status": "open", "detected_at": _hours_ago(6)},
    {"title": "Multiple failed MFA attempts — Raymond Ward", "description": "5 consecutive MFA push denials for Raymond Ward within 10 minutes. Possible MFA fatigue attack or unauthorized access attempt.", "severity": "medium", "category": "risky_login", "user_email": "raymond.ward@acmelawfirm.com", "status": "acknowledged", "detected_at": _hours_ago(18)},
    # Device non-compliance
    {"title": "Critical device compliance failure — PERSONAL-WIN-001", "description": "Unmanaged personal device PERSONAL-WIN-001 is accessing company resources. Device has no encryption, runs Windows 10 19H1, and is not enrolled in MDM.", "severity": "high", "category": "device_noncompliance", "user_email": "raymond.ward@acmelawfirm.com", "status": "open", "detected_at": _days_ago(1)},
    # Inactive accounts
    {"title": "Dormant account with no MFA — Oscar Barnes", "description": "Account oscar.barnes@acmelawfirm.com has been inactive for 90 days and has no MFA configured. Dormant accounts with weak security are a common attack vector.", "severity": "medium", "category": "inactive_account", "user_email": "oscar.barnes@acmelawfirm.com", "status": "open", "detected_at": _days_ago(3)},
    # Backup failure
    {"title": "Backup job missed schedule — Physical Records Archive", "description": "The 'Physical Records Scan Archive' backup job has not completed successfully in 4 days. Last successful backup was 4 days ago. NAS device is reporting low disk space.", "severity": "medium", "category": "backup_failure", "status": "open", "detected_at": _days_ago(2)},
    # Resolved incidents
    {"title": "Phishing email reported by staff", "description": "Staff member reported a phishing email impersonating the firm's managing partner requesting wire transfer approval. Email quarantined. All staff notified.", "severity": "high", "category": "phishing", "status": "resolved", "detected_at": _days_ago(5), "resolved_at": _days_ago(4)},
    {"title": "Stale admin account — former IT contractor", "description": "Active admin account found for IT contractor who left the firm 3 months ago. Account has been disabled and access revoked.", "severity": "high", "category": "inactive_account", "status": "resolved", "detected_at": _days_ago(10), "resolved_at": _days_ago(9)},
]

TASKS_DATA = [
    # Todo tasks
    {"title": "Enable MFA for 5 users without MFA", "description": "Users frank.butler, linda.simmons, paul.foster, donna.cox, and raymond.ward do not have MFA enabled. Enable Microsoft Authenticator for all five accounts.", "priority": "critical", "status": "todo", "assigned_to": "IT Admin", "due_date": now + timedelta(days=2)},
    {"title": "Disable or remediate inactive accounts (5 accounts)", "description": "5 accounts have not been active in 30+ days. Review each account with HR and either disable or verify the user still requires access.", "priority": "high", "status": "todo", "assigned_to": "IT Admin", "due_date": now + timedelta(days=3)},
    {"title": "Enroll PERSONAL-WIN-001 in MDM or block access", "description": "Raymond Ward is using a personal unmanaged device. Either enroll in Microsoft Intune with required security policies or block access until compliant.", "priority": "critical", "status": "todo", "assigned_to": "IT Admin", "due_date": now + timedelta(days=1)},
    {"title": "Fix NAS disk space — Physical Records backup", "description": "The NAS device backing up Physical Records Scan Archive is low on disk space causing backup failures. Add storage or archive old backups to clear space.", "priority": "high", "status": "todo", "assigned_to": "IT Admin", "due_date": now + timedelta(days=1)},
    {"title": "Upgrade ACME-WIN-099 to Windows 11", "description": "Device ACME-WIN-099 (Frank Butler) is running Windows 10 21H1 which is end of life. Upgrade to Windows 11 22H2 and enable BitLocker.", "priority": "high", "status": "todo", "assigned_to": None, "due_date": now + timedelta(days=7)},
    {"title": "Enable BitLocker on ACME-WIN-099", "description": "Frank Butler's laptop does not have BitLocker enabled. This is a critical compliance requirement for all company devices.", "priority": "high", "status": "todo", "assigned_to": None, "due_date": now + timedelta(days=3)},
    {"title": "Conduct security awareness training", "description": "Schedule and conduct phishing simulation and security awareness training for all 50 staff members. Due to recent phishing attempt targeting the firm.", "priority": "medium", "status": "todo", "assigned_to": None, "due_date": now + timedelta(days=14)},
    {"title": "Review and update firewall rules", "description": "Annual review of firewall rules is overdue. Remove unused rules and verify all inbound rules are still needed.", "priority": "medium", "status": "todo", "assigned_to": None, "due_date": now + timedelta(days=21)},
    # In progress tasks
    {"title": "Investigate impossible travel alert — Oscar Barnes", "description": "Reviewing account activity, contacting user, checking if VPN or proxy usage explains the alert. Consider forcing password reset.", "priority": "critical", "status": "in_progress", "assigned_to": "IT Admin", "due_date": now + timedelta(hours=4)},
    {"title": "Upgrade ACME-MAC-088 to macOS 14", "description": "Paul Foster's Mac is running macOS 12.7 (Monterey) which is 2 major versions behind. Scheduled upgrade for this week.", "priority": "medium", "status": "in_progress", "assigned_to": "IT Admin", "due_date": now + timedelta(days=3)},
    {"title": "Deploy conditional access policies — Microsoft Entra ID", "description": "Configuring require-compliant-device and require-MFA conditional access policies in Microsoft Entra ID to prevent unmanaged device access.", "priority": "high", "status": "in_progress", "assigned_to": "IT Admin", "due_date": now + timedelta(days=5)},
    # Done tasks
    {"title": "Disable former IT contractor admin account", "description": "Identified and disabled stale admin account for departed contractor. Completed audit of all admin accounts.", "priority": "critical", "status": "done", "assigned_to": "IT Admin", "due_date": _days_ago(9), "completed_at": _days_ago(9)},
]


async def seed_demo_data() -> None:
    """Seed demo data if the database is empty."""
    async with AsyncSessionLocal() as db:
        # Check if tenant already exists
        result = await db.execute(select(Tenant).where(Tenant.id == TENANT_ID))
        if result.scalar_one_or_none():
            logger.info("Demo data already exists, skipping seed")
            return

        logger.info("Seeding demo data for Acme Law Firm...")

        # Create tenant
        tenant = Tenant(
            id=TENANT_ID,
            name="Acme Law Firm",
            domain="acmelawfirm.com",
            plan="professional",
            last_sync_at=_hours_ago(1),
        )
        db.add(tenant)
        await db.flush()

        # Create users
        for u in USERS_DATA:
            user = User(
                tenant_id=TENANT_ID,
                email=u["email"],
                display_name=u["display_name"],
                mfa_enabled=u["mfa_enabled"],
                mfa_methods=u["mfa_methods"],
                last_sign_in=u["last_sign_in"],
                is_active=True,
                risk_level=u["risk_level"],
                source="microsoft365",
                external_id=str(uuid.uuid4()),
            )
            db.add(user)

        # Create devices
        for d in DEVICES_DATA:
            device = Device(
                tenant_id=TENANT_ID,
                device_name=d["device_name"],
                owner_email=d["owner_email"],
                os_type=d["os_type"],
                os_version=d["os_version"],
                is_compliant=d["is_compliant"],
                encryption_enabled=d["encryption_enabled"],
                last_seen=d["last_seen"],
                compliance_issues=d["compliance_issues"],
                risk_score=d["risk_score"],
                source="microsoft365",
            )
            db.add(device)

        # Create backup jobs
        for b in BACKUP_JOBS_DATA:
            job = BackupJob(
                tenant_id=TENANT_ID,
                name=b["name"],
                target_description=b["target_description"],
                status=b["status"],
                backup_size_gb=b["backup_size_gb"],
                retention_days=b["retention_days"],
                provider=b["provider"],
                last_backup_at=b["last_backup_at"],
                next_backup_at=b.get("next_backup_at"),
                notes=b.get("notes"),
            )
            db.add(job)

        # Create incidents
        for inc in INCIDENTS_DATA:
            incident = Incident(
                tenant_id=TENANT_ID,
                title=inc["title"],
                description=inc["description"],
                severity=inc["severity"],
                category=inc["category"],
                user_email=inc.get("user_email"),
                status=inc["status"],
                detected_at=inc["detected_at"],
                resolved_at=inc.get("resolved_at"),
            )
            db.add(incident)

        # Create tasks
        for t in TASKS_DATA:
            task = Task(
                tenant_id=TENANT_ID,
                title=t["title"],
                description=t["description"],
                priority=t["priority"],
                status=t["status"],
                assigned_to=t.get("assigned_to"),
                due_date=t.get("due_date"),
                completed_at=t.get("completed_at"),
            )
            db.add(task)

        await db.commit()
        logger.info(
            "Demo data seeded: %d users, %d devices, %d backups, %d incidents, %d tasks",
            len(USERS_DATA),
            len(DEVICES_DATA),
            len(BACKUP_JOBS_DATA),
            len(INCIDENTS_DATA),
            len(TASKS_DATA),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_demo_data())
