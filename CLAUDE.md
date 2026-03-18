# CLAUDE.md — CyberShield Control Center

Guidance for Claude Code when working in this repository.

---

## What This Project Is

**CyberShield Control Center** is a full-stack cybersecurity dashboard for small businesses (law firms, medical offices, accounting firms, startups). It gives a single pane of glass for:

- MFA coverage and identity hygiene
- Risky sign-in detection
- Device compliance posture
- Backup health monitoring
- Security incident timeline
- Remediation task board

Target users: IT admins and MSPs managing 10–500 person companies on Microsoft 365 or Google Workspace, without a dedicated security team.

---

## Architecture

```
cybersec-control-center/
├── frontend/          Next.js 14 (App Router) — port 3000
├── backend/           FastAPI (Python) — port 8000
├── docker-compose.yml PostgreSQL 16 + backend + frontend
├── .env               Local env vars (copy from .env.example)
└── .env.example       Template — never commit .env
```

### Backend (`backend/`)

```
app/
├── main.py            FastAPI entry — lifespan, CORS, router mounts
├── config.py          Pydantic Settings — reads from .env
├── database.py        Async SQLAlchemy engine + session factory
├── seed.py            Demo data: "Acme Law Firm", 50 users, 55 devices, 9 backups
├── models/            SQLAlchemy ORM models
│   ├── tenant.py      Org + OAuth tokens (Microsoft/Google)
│   ├── user.py        User, MFA status, risk level, last sign-in
│   ├── device.py      Device posture, compliance, encryption
│   ├── backup.py      Backup jobs, status, schedule
│   ├── incident.py    Security incidents, severity, category, status
│   └── task.py        Remediation tasks, priority, Kanban status
├── schemas/           Pydantic request/response schemas (match models)
├── routers/           FastAPI route handlers
│   ├── dashboard.py   GET /api/dashboard/summary
│   ├── identity.py    /api/identity/users|mfa-summary|inactive-users|sync
│   ├── devices.py     /api/devices
│   ├── backups.py     /api/backups
│   ├── incidents.py   /api/incidents + acknowledge/resolve
│   ├── tasks.py       CRUD /api/tasks
│   └── integrations.py OAuth flows /api/integrations/microsoft|google
├── services/
│   ├── security_score.py  Weighted score: MFA 30pt, incidents 25pt, devices 20pt, backups 15pt, inactive 10pt
│   ├── microsoft_graph.py MS Graph API client (users, risky logins, MFA status)
│   ├── google_admin.py    Google Admin SDK client
│   └── sync_jobs.py       APScheduler — syncs every 30 min
└── middleware/
    ├── auth.py        JWT validation
    └── logging.py     Structured JSON logging (structlog)
```

### Frontend (`frontend/`)

```
app/
├── layout.tsx             Root layout (font, metadata)
├── page.tsx               Redirects → /dashboard
├── dashboard/
│   ├── page.tsx           Main dashboard (score gauge + 5 widgets)
│   ├── identity/page.tsx  User table, MFA coverage, inactive alerts
│   ├── devices/page.tsx   Device posture table
│   ├── backups/page.tsx   Backup job cards
│   ├── incidents/page.tsx Incident timeline with filters
│   └── tasks/page.tsx     Kanban board (Todo/In Progress/Done)
└── settings/
    ├── page.tsx           General settings
    └── integrations/page.tsx  Microsoft 365 + Google Workspace OAuth connect
components/
├── layout/Sidebar.tsx     Dark sidebar (#0F172A), nav links with icons
├── layout/TopNav.tsx      Org name, sync button, alerts
├── layout/AlertBanner.tsx Critical incident banner
└── dashboard/
    ├── SecurityScoreCard.tsx    Animated circular gauge, 0–100
    ├── MFACoverageWidget.tsx    Donut chart + "Fix Now" CTA
    ├── RiskyLoginsWidget.tsx    Count + severity breakdown
    ├── DevicePostureWidget.tsx  Compliant/non-compliant bars
    ├── BackupStatusWidget.tsx   Status pills + last backup time
    └── IncidentTimeline.tsx     Mini feed of recent incidents
lib/
├── types.ts    TypeScript interfaces (User, Device, Incident, Task, etc.)
├── api.ts      Axios client — base URL from NEXT_PUBLIC_API_URL
└── utils.ts    clsx/twMerge, date helpers, risk color helpers
```

---

## Common Commands

### Docker (recommended — runs everything)
```bash
cd C:/Users/keff2/Projects/cybersec-control-center

# Start all services (PostgreSQL + backend + frontend)
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop everything
docker compose down

# Wipe DB and start fresh
docker compose down -v && docker compose up -d
```

### Backend (local dev)
```bash
cd backend

# Setup
python -m venv venv
venv\Scripts\activate      # Windows
python -m pip install -r requirements.txt

# Run (auto-seeds demo data on first start in development mode)
uvicorn app.main:app --reload --port 8000

# Run Alembic migrations manually
alembic upgrade head

# Run tests
pytest tests/ -v

# Seed demo data manually
python -m app.seed
```

### Frontend (local dev)
```bash
cd frontend

# Setup
npm install

# Run dev server
npm run dev

# Type-check
npm run type-check

# Lint
npm run lint

# Production build
npm run build && npm start
```

---

## Environment Variables

Copy `.env.example` → `.env` and fill in values.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | asyncpg PostgreSQL connection string |
| `SECRET_KEY` | Yes | JWT signing key (32-byte hex) |
| `ENVIRONMENT` | Yes | `development` → auto-seeds demo data |
| `FRONTEND_URL` | Yes | CORS origin for Next.js |
| `MICROSOFT_CLIENT_ID` | Optional | Azure AD app for MS Graph sync |
| `MICROSOFT_CLIENT_SECRET` | Optional | Azure AD secret |
| `MICROSOFT_TENANT_ID` | Optional | Azure AD tenant |
| `GOOGLE_CLIENT_ID` | Optional | Google OAuth for Admin SDK |
| `GOOGLE_CLIENT_SECRET` | Optional | Google OAuth secret |
| `NEXTAUTH_SECRET` | Yes (frontend) | NextAuth signing secret |
| `NEXT_PUBLIC_API_URL` | Yes (frontend) | Backend API base URL |

Generate `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API Reference

Base URL: `http://localhost:8000`

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check (DB ping) |
| GET | `/docs` | Swagger UI (interactive) |
| GET | `/api/dashboard/summary` | Security score + all widget data |
| GET | `/api/identity/users` | Paginated user list with MFA/risk status |
| GET | `/api/identity/mfa-summary` | MFA coverage stats |
| GET | `/api/identity/inactive-users` | Users inactive 30+ days |
| POST | `/api/identity/sync` | Trigger manual sync from provider |
| GET | `/api/devices` | Device posture list |
| GET | `/api/backups` | Backup jobs and status |
| GET | `/api/incidents` | Incident timeline (filter: severity, status, category) |
| POST | `/api/incidents/{id}/acknowledge` | Acknowledge incident |
| POST | `/api/incidents/{id}/resolve` | Resolve incident |
| GET | `/api/tasks` | Task list (filter: status, priority) |
| POST | `/api/tasks` | Create remediation task |
| PATCH | `/api/tasks/{id}` | Update task status/assignee |
| DELETE | `/api/tasks/{id}` | Delete task |
| GET | `/api/integrations/status` | Which integrations are connected |
| GET | `/api/integrations/microsoft/authorize` | Start MS OAuth flow |
| GET | `/api/integrations/microsoft/callback` | MS OAuth callback |
| GET | `/api/integrations/google/authorize` | Start Google OAuth flow |
| GET | `/api/integrations/google/callback` | Google OAuth callback |

---

## Data Models (Key Fields)

### Security Score (0–100, weighted)
- MFA coverage ≥ 90%: 30 pts
- No critical/high incidents open: 25 pts
- Device compliance ≥ 90%: 20 pts
- All backups healthy: 15 pts
- No inactive accounts: 10 pts

### Incident Categories
`risky_login` | `mfa_bypass` | `inactive_account` | `device_noncompliance` | `backup_failure` | `phishing`

### Incident Severity
`info` → `low` → `medium` → `high` → `critical`

### Task Status (Kanban)
`todo` → `in_progress` → `done` | `dismissed`

---

## Microsoft 365 Integration Setup

1. Go to [Azure Portal → App Registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps)
2. New registration → set redirect URI: `http://localhost:8000/api/integrations/microsoft/callback`
3. Add API permissions: `User.Read.All`, `AuditLog.Read.All`, `IdentityRiskyUser.Read.All`, `UserAuthenticationMethod.Read.All`
4. Grant admin consent
5. Add `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`, `MICROSOFT_TENANT_ID` to `.env`

## Google Workspace Integration Setup

1. Go to [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 client → redirect URI: `http://localhost:8000/api/integrations/google/callback`
3. Enable APIs: Admin SDK, Directory API
4. Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` to `.env`

---

## Demo Data (Seeded Automatically)

When `ENVIRONMENT=development`, startup auto-seeds "Acme Law Firm":
- **50 users**: 45 with MFA enabled, 5 inactive
- **55 devices**: 48 compliant, 7 non-compliant
- **9 backup jobs**: 8 healthy, 1 warning
- **8 incidents**: mix of risky logins, inactive accounts, device issues
- **12 tasks**: open remediation items

Demo data is idempotent — re-running seed skips if data exists.

---

## Design System

| Token | Value | Usage |
|---|---|---|
| Sidebar bg | `#0F172A` (slate-900) | Sidebar background |
| Primary | `#2563EB` (blue-600) | Buttons, links, active nav |
| Critical | `#DC2626` (red-600) | High/critical severity |
| Warning | `#D97706` (amber-600) | Medium severity, warnings |
| Healthy | `#16A34A` (green-600) | Healthy status |
| Score < 50 | red | Security score gauge |
| Score 50–75 | yellow | Security score gauge |
| Score > 75 | green | Security score gauge |

UI library: Radix UI primitives + Tailwind CSS. Icons: `lucide-react`. Charts: `recharts`.

---

## Production Roadmap

Future phases planned after MVP:

1. **Endpoint integrations** — MDM/EDR agent data (Intune, Jamf, CrowdStrike)
2. **Conditional access recommendations** — auto-suggest policy hardening
3. **Automated offboarding checks** — detect terminated users still active
4. **Vendor risk tracking** — third-party SaaS inventory and risk scoring
5. **Compliance export** — SOC 2 / HIPAA evidence package PDF export
6. **MSP multi-tenant** — manage multiple orgs from one login
7. **Alerting** — email/Slack/PagerDuty for critical incidents

---

## Known Issues / TODOs

- OAuth token refresh not implemented (tokens expire after 1 hour without refresh)
- `microsoft_graph.py` and `google_admin.py` have full auth flows but sync logic returns structured mock data until real Graph API calls are wired to DB writes
- No rate limiting on API endpoints (add in production)
- No pagination cursor on large datasets (uses offset/limit)
- `NEXTAUTH_SECRET` must be set even without auth provider configured

---

## Security Notes

- Never commit `.env` — it's in `.gitignore`
- `SECRET_KEY` must be ≥ 32 bytes of random hex in production
- OAuth tokens stored in `tenant.microsoft_access_token` should be encrypted at rest (column-level encryption via `cryptography` lib is imported but not applied yet)
- Change default Docker postgres password before any cloud deployment
