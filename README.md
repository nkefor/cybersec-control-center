<div align="center">

# CyberShield Control Center

**Unified cybersecurity visibility for small businesses — without a dedicated security team.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql)](https://postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://docker.com)

*Law firms · Medical offices · Accounting firms · Startups · Retailers*

</div>

---

## The Problem

A 50-person company using Microsoft 365, Google Workspace, and cloud apps has no single view of their security posture. They cannot afford a full enterprise security platform, but they still face the same threats: phishing, weak MFA, inactive accounts, unencrypted devices, missed backups.

**CyberShield gives them one dashboard to see everything and act on it.**

---

## What It Does

| Capability | What You Get |
|---|---|
| **Security Score** | Weighted 0–100 score across 5 control domains, updated every 30 minutes |
| **Identity & MFA** | Full user roster, MFA coverage %, inactive account detection, risky sign-in alerts |
| **Device Posture** | Compliance status, encryption, OS breakdown for every managed device |
| **Backup Health** | All backup jobs in one view — healthy, warning, or critical with last-run timestamps |
| **Incident Timeline** | Auto-detected security events with severity, acknowledge, and resolve workflow |
| **Task Board** | Kanban-style remediation tasks auto-generated from detected issues |
| **M365 Integration** | Live sync via Microsoft Graph API — users, MFA methods, risky sign-ins |
| **Google Workspace** | Live sync via Google Admin SDK — users, login activity |

---

## Architecture

### High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CYBERSHIELD CONTROL CENTER                       │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      BROWSER / CLIENT                           │   │
│   │                                                                 │   │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │   │
│   │   │  Dashboard   │  │  Identity /  │  │  Tasks / Incidents / │ │   │
│   │   │  Score +     │  │  Devices /   │  │  Settings /          │ │   │
│   │   │  Widgets     │  │  Backups     │  │  Integrations        │ │   │
│   │   └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │   │
│   │          └─────────────────┴──────────────────────┘             │   │
│   │                            │  HTTP/JSON                         │   │
│   └────────────────────────────┼────────────────────────────────────┘   │
│                                │                                         │
│   ┌────────────────────────────▼────────────────────────────────────┐   │
│   │                   NEXT.JS 14  (port 3000)                       │   │
│   │                   App Router · TypeScript · Tailwind CSS        │   │
│   │                                                                 │   │
│   │   ┌────────────┐  ┌────────────┐  ┌────────────┐               │   │
│   │   │  Dashboard │  │  Identity  │  │  Devices   │  ...pages     │   │
│   │   │  /page.tsx │  │  /page.tsx │  │  /page.tsx │               │   │
│   │   └────────────┘  └────────────┘  └────────────┘               │   │
│   │   ┌─────────────────────────────────────────────┐               │   │
│   │   │  Components: SecurityScoreCard · MFAWidget  │               │   │
│   │   │  RiskyLoginsWidget · BackupWidget · Kanban  │               │   │
│   │   └─────────────────────────────────────────────┘               │   │
│   │   ┌───────────────┐  ┌────────────────────────────┐             │   │
│   │   │  lib/api.ts   │  │  lib/types.ts              │             │   │
│   │   │  fetch client │  │  TypeScript interfaces      │             │   │
│   │   └───────┬───────┘  └────────────────────────────┘             │   │
│   └───────────┼─────────────────────────────────────────────────────┘   │
│               │  REST API  (CORS-secured)                                │
│   ┌───────────▼─────────────────────────────────────────────────────┐   │
│   │                    FASTAPI  (port 8000)                         │   │
│   │                    Python 3.12 · Async · Uvicorn                │   │
│   │                                                                 │   │
│   │  ┌─────────────────────────────────────────────────────────┐   │   │
│   │  │                      ROUTERS                            │   │   │
│   │  │  /api/dashboard  /api/identity  /api/devices            │   │   │
│   │  │  /api/backups    /api/incidents /api/tasks              │   │   │
│   │  │  /api/integrations  /health                             │   │   │
│   │  └──────────────────────────┬──────────────────────────────┘   │   │
│   │                             │                                   │   │
│   │  ┌──────────────────────────▼──────────────────────────────┐   │   │
│   │  │                      SERVICES                           │   │   │
│   │  │  SecurityScoreService  ·  MicrosoftGraphService         │   │   │
│   │  │  GoogleAdminService    ·  SyncJobService                │   │   │
│   │  └──────────────────────────┬──────────────────────────────┘   │   │
│   │                             │                                   │   │
│   │  ┌──────────────────────────▼──────────────────────────────┐   │   │
│   │  │               SQLAlchemy 2.0 (async)                    │   │   │
│   │  │               Alembic Migrations                        │   │   │
│   │  └──────────────────────────┬──────────────────────────────┘   │   │
│   │                             │                                   │   │
│   │  ┌──────────────────────────▼──────────────────────────────┐   │   │
│   │  │             APScheduler  (every 30 min)                 │   │   │
│   │  │             Per-tenant isolated sync sessions           │   │   │
│   │  └─────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│               │                                                          │
│   ┌───────────▼──────────────┐                                          │
│   │   PostgreSQL 16          │                                          │
│   │   ─────────────────────  │                                          │
│   │   tenants                │                                          │
│   │   users                  │                                          │
│   │   devices                │                                          │
│   │   backup_jobs            │                                          │
│   │   incidents              │                                          │
│   │   tasks                  │                                          │
│   └──────────────────────────┘                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Data Flow — Live Sync

```
  Microsoft 365                    CyberShield Backend                  Dashboard
  ─────────────                    ───────────────────                  ─────────

  Azure AD ──────── OAuth2 ──────► /api/integrations/microsoft/authorize
                                   /api/integrations/microsoft/callback ◄── Token stored
                                            │
                                   APScheduler (every 30 min)
                                            │
                                   ┌────────▼─────────┐
                                   │  MicrosoftGraph  │
                                   │  Service         │
                                   └────────┬─────────┘
                                            │
                   ┌────────────────────────┼──────────────────────────┐
                   │                        │                          │
            GET /users              GET /riskySignIns       GET /userRegDetails
                   │                        │                          │
                   ▼                        ▼                          ▼
            Upsert users DB       Create Incident rows        Update mfa_enabled,
            (email, name,         if new signin_id            mfa_methods columns
             is_active,           detected (severity          on user rows
             last_sign_in)        mapped from riskLevel)
                   │                        │                          │
                   └────────────────────────┴──────────────────────────┘
                                            │
                                   Auto-task generation
                                   (if >5 users lack MFA → create Task)
                                            │
                                   tenant.last_sync_at = now()
                                            │
                                   GET /api/dashboard/summary ◄──────── Browser polls
                                   SecurityScoreService recalculates
                                            │
                                   Score returned ──────────────────────► Gauge animates
```

---

### Security Score Algorithm

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                    SECURITY SCORE  (0 – 100)                        │
  ├───────────────────┬──────────┬──────────────────────────────────────┤
  │  Control Domain   │  Weight  │  Scoring Logic                       │
  ├───────────────────┼──────────┼──────────────────────────────────────┤
  │  MFA Coverage     │   30 pt  │  (mfa_enabled / total_active) × 30  │
  │                   │          │  e.g. 45/50 = 90% → 27 pts          │
  ├───────────────────┼──────────┼──────────────────────────────────────┤
  │  Open Incidents   │   25 pt  │  0 critical/high  → 25 pts          │
  │                   │          │  1–2 critical     → 15 pts          │
  │                   │          │  3–5 critical     →  5 pts          │
  │                   │          │  >5 critical      →  0 pts          │
  ├───────────────────┼──────────┼──────────────────────────────────────┤
  │  Device Compliance│   20 pt  │  (compliant / total) × 20           │
  │                   │          │  e.g. 48/55 = 87% → 17 pts          │
  ├───────────────────┼──────────┼──────────────────────────────────────┤
  │  Backup Health    │   15 pt  │  (healthy / total) × 15             │
  │                   │          │  e.g. 8/9 = 89%   → 13 pts          │
  ├───────────────────┼──────────┼──────────────────────────────────────┤
  │  Active Accounts  │   10 pt  │  inactive_rate < 5%  → 10 pts       │
  │                   │          │  inactive_rate < 10% →  7 pts       │
  │                   │          │  inactive_rate < 20% →  3 pts       │
  │                   │          │  (NULL last_sign_in = inactive)     │
  ├───────────────────┼──────────┼──────────────────────────────────────┤
  │  TOTAL            │  100 pt  │  min(max(sum, 0), 100)              │
  └───────────────────┴──────────┴──────────────────────────────────────┘

  Score ranges:   ██ 0–49 CRITICAL (red)   ██ 50–74 AT RISK (yellow)   ██ 75–100 HEALTHY (green)
```

---

### Database Schema

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                          DATABASE SCHEMA                             │
  └──────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────┐
  │       tenants        │
  ├─────────────────────┤
  │ id (PK, UUID)       │◄──────────────────────────────────────────────┐
  │ name                │                                               │
  │ domain              │                                               │
  │ plan                │  enum: starter / professional / msp          │
  │ microsoft_tenant_id │                                               │
  │ microsoft_access_   │  encrypted OAuth token                       │
  │   token             │                                               │
  │ google_domain       │                                               │
  │ google_credentials  │  encrypted JSON credentials                  │
  │ last_sync_at        │                                               │
  │ created_at          │                                               │
  └─────────────────────┘                                               │
                                                                        │
  ┌──────────────────────┐  ┌──────────────────────┐                   │
  │        users         │  │       devices        │                   │
  ├──────────────────────┤  ├──────────────────────┤                   │
  │ id (PK, UUID)        │  │ id (PK, UUID)        │                   │
  │ tenant_id (FK) ──────┼──┤ tenant_id (FK) ──────┼───────────────────┘
  │ email                │  │ device_name          │
  │ display_name         │  │ owner_email          │
  │ mfa_enabled (bool)   │  │ os_type              │  enum: windows/macos/
  │ mfa_methods (JSON)   │  │ os_version           │         linux/ios/android
  │ last_sign_in         │  │ is_compliant (bool)  │
  │ is_active (bool)     │  │ encryption_enabled   │
  │ risk_level           │  │ last_seen            │
  │ source               │  │ compliance_issues    │  JSON array of strings
  │ external_id          │  │ risk_score (0-100)   │
  │ created_at           │  │ source               │
  │ updated_at           │  │ created_at           │
  └──────────────────────┘  └──────────────────────┘

  ┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────────┐
  │     backup_jobs      │  │      incidents       │  │      tasks        │
  ├──────────────────────┤  ├──────────────────────┤  ├───────────────────┤
  │ id (PK, UUID)        │  │ id (PK, UUID)        │  │ id (PK, UUID)     │
  │ tenant_id (FK)       │  │ tenant_id (FK)       │  │ tenant_id (FK)    │
  │ name                 │  │ title                │  │ title             │
  │ target_description   │  │ description          │  │ description       │
  │ last_backup_at       │  │ severity             │  │ priority          │
  │ next_backup_at       │  │  enum: info/low/     │  │  enum: low/medium/│
  │ status               │  │        medium/high/  │  │        high/      │
  │  enum: healthy/      │  │        critical      │  │        critical   │
  │         warning/     │  │ category             │  │ status            │
  │         critical/    │  │  enum: risky_login/  │  │  enum: todo/      │
  │         unknown      │  │  mfa_bypass/         │  │  in_progress/     │
  │ backup_size_gb       │  │  inactive_account/   │  │  done/dismissed   │
  │ retention_days       │  │  device_noncompliance│  │ assigned_to       │
  │ provider             │  │  backup_failure/     │  │ related_incident_ │
  │ notes                │  │  phishing            │  │   id (FK)         │
  │ created_at           │  │ user_email           │  │ due_date          │
  │ updated_at           │  │ device_id (FK)       │  │ completed_at      │
  └──────────────────────┘  │ status               │  │ created_at        │
                             │  enum: open/         │  │ updated_at        │
                             │  acknowledged/       │  └───────────────────┘
                             │  resolved            │
                             │ detected_at          │
                             │ resolved_at          │
                             │ source_data (JSONB)  │
                             └──────────────────────┘
```

---

### Frontend Page Map

```
  http://localhost:3000
  │
  └── /dashboard                    ← Main dashboard
  │     ├── Security Score Gauge    (animated 0–100 circle)
  │     ├── MFA Coverage Widget     (donut chart + "Fix Now" CTA)
  │     ├── Risky Logins Widget     (count + severity breakdown)
  │     ├── Device Posture Widget   (compliant/non-compliant bars)
  │     ├── Backup Status Widget    (status pills + last backup)
  │     └── Incident Timeline       (mini feed of recent events)
  │
  ├── /dashboard/identity           ← Identity & Access Management
  │     ├── MFA Coverage Progress Bar
  │     ├── Inactive Accounts Alert Banner
  │     └── User Table              (email, MFA badge, risk, last login, status)
  │
  ├── /dashboard/devices            ← Device Posture
  │     ├── Posture Summary Cards   (compliance %, encryption %)
  │     ├── OS Breakdown            (Windows / macOS / Linux / Mobile)
  │     └── Device Table            (name, owner, OS, compliant, encrypted, risk score)
  │
  ├── /dashboard/backups            ← Backup Health
  │     ├── Status Summary          (healthy / warning / critical counts)
  │     └── Backup Job Cards        (name, provider, last run, size, schedule)
  │
  ├── /dashboard/incidents          ← Incident Timeline
  │     ├── Severity Filter Tabs    (all / critical / high / medium / info)
  │     ├── Status Filter           (open / acknowledged / resolved)
  │     └── Incident Cards          (icon, title, user, time, status + ack/resolve)
  │
  ├── /dashboard/tasks              ← Remediation Task Board
  │     ├── Priority Filter
  │     ├── + New Task Button       (modal form)
  │     └── Kanban Board
  │           ├── To Do column
  │           ├── In Progress column
  │           └── Done column
  │
  └── /settings/integrations        ← Provider Connections
        ├── Microsoft 365 Card      (Connect / Disconnect, last sync, scopes)
        └── Google Workspace Card   (Connect / Disconnect, last sync, domain)
```

---

### API Routes Reference

```
  BASE URL: http://localhost:8000

  ┌──────────────────────────────────────────────────────────────┐
  │  DASHBOARD                                                   │
  │  GET  /api/dashboard/summary          Full metrics payload   │
  ├──────────────────────────────────────────────────────────────┤
  │  IDENTITY                                                    │
  │  GET  /api/identity/users             Paginated user list    │
  │  GET  /api/identity/mfa-summary       MFA coverage stats     │
  │  GET  /api/identity/inactive-users    Inactive 30+ days      │
  │  POST /api/identity/sync              Trigger manual sync    │
  ├──────────────────────────────────────────────────────────────┤
  │  DEVICES                                                     │
  │  GET  /api/devices                    Device list            │
  │  GET  /api/devices/posture-summary    Compliance stats       │
  ├──────────────────────────────────────────────────────────────┤
  │  BACKUPS                                                     │
  │  GET  /api/backups                    Backup job list        │
  │  POST /api/backups                    Create backup entry    │
  │  PATCH /api/backups/{id}              Update backup          │
  │  DELETE /api/backups/{id}             Remove backup          │
  ├──────────────────────────────────────────────────────────────┤
  │  INCIDENTS                                                   │
  │  GET  /api/incidents                  Incident timeline      │
  │  POST /api/incidents/{id}/acknowledge Mark acknowledged      │
  │  POST /api/incidents/{id}/resolve     Mark resolved          │
  ├──────────────────────────────────────────────────────────────┤
  │  TASKS                                                       │
  │  GET  /api/tasks                      Task list              │
  │  POST /api/tasks                      Create task            │
  │  PATCH /api/tasks/{id}                Update task            │
  │  DELETE /api/tasks/{id}               Delete task            │
  ├──────────────────────────────────────────────────────────────┤
  │  INTEGRATIONS                                                │
  │  GET  /api/integrations/status                               │
  │  GET  /api/integrations/microsoft/authorize  OAuth start     │
  │  GET  /api/integrations/microsoft/callback   OAuth return    │
  │  DELETE /api/integrations/microsoft/disconnect               │
  │  GET  /api/integrations/google/authorize     OAuth start     │
  │  GET  /api/integrations/google/callback      OAuth return    │
  │  DELETE /api/integrations/google/disconnect                  │
  ├──────────────────────────────────────────────────────────────┤
  │  SYSTEM                                                      │
  │  GET  /health                         DB ping + version      │
  │  GET  /docs                           Swagger UI             │
  │  GET  /redoc                          ReDoc UI               │
  └──────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Option A — Docker Compose (Recommended, 5 minutes)

```bash
# Clone the repo
git clone https://github.com/nkefor/cybersec-control-center.git
cd cybersec-control-center

# Copy and configure environment
cp .env.example .env

# Start PostgreSQL + backend + frontend
docker compose up -d

# Wait ~30s for containers to initialize, then open:
# Dashboard → http://localhost:3000
# API docs  → http://localhost:8000/docs
```

Demo data seeds automatically on first start. No configuration required.

### Option B — Local Development

**Prerequisites:** Python 3.12+, Node.js 18+, Docker (for PostgreSQL)

**Step 1 — Start PostgreSQL**
```bash
docker run -d \
  --name cybersec-pg \
  -e POSTGRES_DB=cybersec \
  -e POSTGRES_USER=cybersec \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:16-alpine
```

**Step 2 — Backend**
```bash
cd backend

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

python -m pip install -r requirements.txt

cp ../.env.example ../.env
# Edit .env — DATABASE_URL and SECRET_KEY at minimum

uvicorn app.main:app --reload --port 8000
# API starts at http://localhost:8000
# Demo data seeds automatically (ENVIRONMENT=development)
```

**Step 3 — Frontend**
```bash
cd frontend

npm install

# Set API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local
echo "NEXTAUTH_URL=http://localhost:3000" >> .env.local
echo "NEXTAUTH_SECRET=dev-secret-change-me" >> .env.local

npm run dev
# Dashboard at http://localhost:3000
```

---

## Environment Variables

Copy `.env.example` → `.env` and fill in values.

```bash
# ── Database ──────────────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://cybersec:password@localhost:5432/cybersec

# ── Security ──────────────────────────────────────────────────────────────
# Generate: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-secret-key-here

# ── Application ───────────────────────────────────────────────────────────
ENVIRONMENT=development          # set to "production" for prod
LOG_LEVEL=INFO
FRONTEND_URL=http://localhost:3000
SYNC_INTERVAL_MINUTES=30

# ── Microsoft 365 (optional — for live sync) ──────────────────────────────
# Register at: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps
# Redirect URI: http://localhost:8000/api/integrations/microsoft/callback
# Permissions: User.Read.All, AuditLog.Read.All,
#              UserAuthenticationMethod.Read.All, IdentityRiskyUser.Read.All
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_TENANT_ID=

# ── Google Workspace (optional — for live sync) ───────────────────────────
# Create at: https://console.cloud.google.com/apis/credentials
# Enable: Admin SDK, Reports API, Directory API
# Redirect URI: http://localhost:8000/api/integrations/google/callback
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# ── Next.js ───────────────────────────────────────────────────────────────
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Demo Data

On first startup in development mode, the backend seeds a realistic demo tenant:

```
Acme Law Firm
├── Users: 50 total
│   ├── 45 with MFA enabled  (90% coverage)
│   ├── 5  without MFA       → flagged in dashboard
│   └── 5  inactive 30+ days → appear in inactive alert
│
├── Devices: 55 total
│   ├── 48 compliant
│   └── 7  non-compliant    → issues listed per device
│
├── Backup Jobs: 9
│   ├── 8  healthy           (last run < 24h)
│   └── 1  warning           (last run > 48h)
│
├── Incidents: 8
│   ├── 2 high severity  risky logins
│   ├── 3 medium severity risky logins
│   ├── 2 device non-compliance alerts
│   └── 1 backup failure warning
│
└── Tasks: 12 open
    ├── 4 critical
    ├── 5 high
    └── 3 medium
```

Security score for this demo: **~72 / 100** (AT RISK — yellow)

---

## Connecting Microsoft 365

```
1. Azure Portal → App Registrations → New registration
   Name: CyberShield
   Redirect URI: http://localhost:8000/api/integrations/microsoft/callback

2. API Permissions → Add:
   ✓ User.Read.All                       (list all users)
   ✓ AuditLog.Read.All                   (sign-in logs)
   ✓ UserAuthenticationMethod.Read.All   (MFA method status)
   ✓ IdentityRiskyUser.Read.All          (risky sign-in detection)
   → Grant admin consent

3. Certificates & Secrets → New client secret → Copy value

4. Add to .env:
   MICROSOFT_CLIENT_ID=<Application (client) ID>
   MICROSOFT_CLIENT_SECRET=<secret value>
   MICROSOFT_TENANT_ID=<Directory (tenant) ID>

5. Settings → Integrations → Connect Microsoft 365 → Authorize
```

## Connecting Google Workspace

```
1. Google Cloud Console → APIs & Services → Credentials
   → Create OAuth 2.0 Client ID (Web application)
   Redirect URI: http://localhost:8000/api/integrations/google/callback

2. Enable APIs:
   ✓ Admin SDK API
   ✓ Google Workspace Directory API

3. Add to .env:
   GOOGLE_CLIENT_ID=<client ID>
   GOOGLE_CLIENT_SECRET=<client secret>

4. Settings → Integrations → Connect Google Workspace → Authorize
```

---

## Project Structure

```
cybersec-control-center/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  FastAPI entry — lifespan, CORS, routers
│   │   ├── config.py                Pydantic Settings — reads from .env
│   │   ├── database.py              Async SQLAlchemy engine + session factory
│   │   ├── seed.py                  Demo data — idempotent, runs on dev startup
│   │   │
│   │   ├── models/                  SQLAlchemy ORM (mapped columns)
│   │   │   ├── tenant.py            Org config + OAuth tokens
│   │   │   ├── user.py              Users, MFA, risk level, source
│   │   │   ├── device.py            Device posture, compliance, encryption
│   │   │   ├── backup.py            Backup jobs, schedule, status
│   │   │   ├── incident.py          Security events, severity, category
│   │   │   └── task.py              Remediation tasks, Kanban status
│   │   │
│   │   ├── schemas/                 Pydantic request/response schemas
│   │   │   ├── dashboard.py         DashboardSummary response
│   │   │   ├── identity.py          User, MFASummary, InactiveUser
│   │   │   ├── devices.py           Device, DevicePostureSummary
│   │   │   ├── backups.py           BackupJob, BackupListResponse
│   │   │   ├── incidents.py         Incident, IncidentListResponse
│   │   │   └── tasks.py             Task, TaskCreate, TaskUpdate
│   │   │
│   │   ├── routers/                 FastAPI route handlers
│   │   │   ├── dashboard.py         GET /api/dashboard/summary
│   │   │   ├── identity.py          /api/identity/*
│   │   │   ├── devices.py           /api/devices/*
│   │   │   ├── backups.py           /api/backups/*
│   │   │   ├── incidents.py         /api/incidents/*
│   │   │   ├── tasks.py             /api/tasks/* (full CRUD)
│   │   │   └── integrations.py      /api/integrations/* (OAuth flows)
│   │   │
│   │   ├── services/
│   │   │   ├── security_score.py    Weighted score calculator
│   │   │   ├── microsoft_graph.py   MS Graph API client (users, risky logins)
│   │   │   ├── google_admin.py      Google Admin SDK client
│   │   │   └── sync_jobs.py         APScheduler — per-tenant isolated sessions
│   │   │
│   │   └── middleware/
│   │       ├── auth.py              JWT validation + tenant extraction
│   │       └── logging.py           Structured JSON logging (structlog)
│   │
│   ├── alembic/                     Database migrations
│   │   └── versions/001_initial.py  Initial schema
│   ├── tests/                       pytest test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
│
├── frontend/
│   ├── app/                         Next.js 14 App Router
│   │   ├── layout.tsx               Root layout (font, metadata)
│   │   ├── page.tsx                 Root → redirects to /dashboard
│   │   ├── dashboard/
│   │   │   ├── page.tsx             Main dashboard (score + widgets)
│   │   │   ├── identity/page.tsx    User table + MFA coverage
│   │   │   ├── devices/page.tsx     Device posture table
│   │   │   ├── backups/page.tsx     Backup job cards
│   │   │   ├── incidents/page.tsx   Incident timeline
│   │   │   └── tasks/page.tsx       Kanban task board
│   │   └── settings/
│   │       ├── page.tsx             General settings
│   │       └── integrations/        M365 + Google OAuth connect UI
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx          Dark nav sidebar (#0F172A)
│   │   │   ├── TopNav.tsx           Header + sync button
│   │   │   └── AlertBanner.tsx      Critical incident banner
│   │   └── dashboard/
│   │       ├── SecurityScoreCard.tsx     Animated circular gauge
│   │       ├── MFACoverageWidget.tsx     Donut chart + Fix Now CTA
│   │       ├── RiskyLoginsWidget.tsx     Count + severity breakdown
│   │       ├── DevicePostureWidget.tsx   Compliance bars
│   │       ├── BackupStatusWidget.tsx    Status pills + last run
│   │       └── IncidentTimeline.tsx      Mini recent events feed
│   │
│   ├── lib/
│   │   ├── api.ts                   fetch wrapper + typed API clients
│   │   ├── types.ts                 TypeScript interfaces (mirrors schemas)
│   │   └── utils.ts                 clsx, date helpers, risk colors
│   │
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
│
├── docker-compose.yml               PostgreSQL + backend + frontend
├── .env.example                     All variables documented
├── CLAUDE.md                        AI assistant context file
└── README.md
```

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Frontend framework | Next.js | 14.1 | App Router SSR/CSR |
| UI language | TypeScript | 5.x | Type safety |
| Styling | Tailwind CSS | 3.4 | Utility-first CSS |
| Charts | Recharts | 2.10 | Security score gauge + donut |
| Icons | Lucide React | 0.309 | Consistent icon set |
| Components | Radix UI | latest | Accessible primitives |
| Backend framework | FastAPI | 0.109 | Async REST API |
| Language | Python | 3.12 | Backend runtime |
| ORM | SQLAlchemy | 2.0 | Async database layer |
| Migrations | Alembic | 1.13 | Schema versioning |
| Database | PostgreSQL | 16 | Primary data store |
| Scheduler | APScheduler | 3.10 | Background sync jobs |
| Auth (frontend) | NextAuth.js | 4.24 | Session management |
| Auth (API) | python-jose | 3.3 | JWT validation |
| MS integration | MSAL | 1.26 | Microsoft OAuth2 + Graph |
| Google integration | google-auth | 2.26 | Google OAuth2 + Admin SDK |
| Logging | structlog | 24.1 | Structured JSON logs |
| Container | Docker Compose | v2 | Local dev orchestration |
| Testing | pytest + httpx | 7.4 | Async API tests |

---

## Running Tests

```bash
cd backend

# Activate virtual environment first
venv\Scripts\activate  # Windows

# Run all tests
pytest tests/ -v

# Run specific suite
pytest tests/test_dashboard.py -v
pytest tests/test_tasks.py -v

# With coverage
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Production Deployment Checklist

```
Security
  ☐ Rotate SECRET_KEY:     python -c "import secrets; print(secrets.token_hex(32))"
  ☐ Rotate NEXTAUTH_SECRET: same command
  ☐ Set ENVIRONMENT=production  (disables demo seeding)
  ☐ Enable HTTPS (required for OAuth redirect URIs)
  ☐ Update OAuth redirect URIs in Azure / Google Console to production domain
  ☐ Remove default PostgreSQL password

Infrastructure
  ☐ Use managed PostgreSQL (AWS RDS, Cloud SQL, Supabase, Neon)
  ☐ Set DATABASE_URL connection pooling (PgBouncer or asyncpg pool config)
  ☐ Deploy backend behind a reverse proxy (Nginx / Caddy)
  ☐ Deploy frontend to Vercel, AWS Amplify, or serve via Nginx
  ☐ Configure health check on /health for load balancer

Observability
  ☐ Ship structured JSON logs to CloudWatch / Datadog / Grafana Loki
  ☐ Add OpenTelemetry instrumentation (optional, planned)
  ☐ Set up uptime monitoring on /health endpoint

Scaling
  ☐ Increase SYNC_INTERVAL_MINUTES based on API rate limits
  ☐ Add Redis for session/cache layer (optional for MVP)
  ☐ Enable read replicas for reporting queries
```

---

## Roadmap

| Phase | Feature | Status |
|---|---|---|
| MVP | Dashboard, identity, devices, backups, incidents, tasks | ✅ Complete |
| MVP | Microsoft 365 OAuth + Graph API sync | ✅ Complete |
| MVP | Google Workspace OAuth + Admin SDK sync | ✅ Complete |
| MVP | Background sync scheduler | ✅ Complete |
| Next | Endpoint integrations (Intune, Jamf, CrowdStrike) | Planned |
| Next | Conditional access policy recommendations | Planned |
| Next | Automated offboarding checks for terminated users | Planned |
| Next | Vendor / SaaS risk tracking | Planned |
| Next | SOC 2 / HIPAA compliance evidence export (PDF) | Planned |
| Next | MSP multi-tenant dashboard | Planned |
| Next | Email + Slack + PagerDuty alerting | Planned |
| Next | OpenTelemetry + Grafana observability | Planned |

---

## Monetization Model

| Plan | Target | Pricing | Includes |
|---|---|---|---|
| **Starter** | 1–25 users | $8/user/mo | Dashboard + M365/Google sync |
| **Professional** | 26–200 users | $12/user/mo | Starter + compliance exports + alerting |
| **MSP** | Managed service providers | $5/user/mo (bulk) | Multi-tenant + white-label + API |

---

## Contributing

```bash
# 1. Fork the repo
# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make changes, run tests
cd backend && pytest tests/ -v
cd frontend && npm run type-check && npm run lint

# 4. Commit with conventional commit message
git commit -m "feat: add vendor risk tracking module"

# 5. Push and open a PR
git push origin feature/your-feature-name
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with FastAPI · Next.js · PostgreSQL

*Giving small businesses the security visibility that enterprise companies take for granted.*

</div>
