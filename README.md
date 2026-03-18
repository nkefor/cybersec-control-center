# CyberShield Control Center

A production-quality cybersecurity dashboard for small businesses (law firms, medical offices, accounting firms). Get unified visibility into MFA coverage, device compliance, backup health, and security incidents without a dedicated security team.

## Features

- **Security Score** — Weighted 0-100 score across MFA, incidents, device compliance, backups, and inactive users
- **Identity Dashboard** — User list with MFA status, risk levels, inactive account detection
- **Device Posture** — Compliance tracking, encryption status, OS breakdown
- **Backup Health** — Monitor all backup jobs with status, size, and schedule
- **Incident Timeline** — Security alerts with acknowledge/resolve workflow
- **Task Board** — Kanban-style remediation task management
- **Microsoft 365 Integration** — Sync users, MFA status, and risky sign-ins via Graph API
- **Google Workspace Integration** — Sync users and login activity via Admin SDK

## Quick Start (5 minutes)

### Option A: Docker Compose (Recommended)

```bash
# 1. Clone / enter directory
cd C:/Users/keff2/Projects/cybersec-control-center

# 2. Copy env file
cp .env.example .env

# 3. Start everything (PostgreSQL + API + Frontend)
docker compose up -d

# 4. Open browser
# Frontend: http://localhost:3000
# API docs:  http://localhost:8000/docs
```

### Option B: Local Development

#### Backend (Python FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt

# Start PostgreSQL (Docker)
docker run -d \
  --name cybersec-postgres \
  -e POSTGRES_DB=cybersec \
  -e POSTGRES_USER=cybersec \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:16-alpine

# Copy env and start API
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

The API auto-creates tables and seeds demo data on first start.

#### Frontend (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at http://localhost:3000

## Demo Data

On first startup (development mode), the API seeds **Acme Law Firm** demo data:
- 50 users (45 with MFA, 5 without, 5 inactive)
- 55 devices (48 compliant, 7 non-compliant)
- 9 backup jobs (8 healthy, 1 warning)
- 8 security incidents (risky logins, device issues, backup failure)
- 12 remediation tasks across all priorities

## API Documentation

Interactive API docs available at http://localhost:8000/docs (Swagger UI)

Key endpoints:
```
GET  /api/dashboard/summary       — Dashboard metrics
GET  /api/identity/users          — User list with MFA status
GET  /api/identity/mfa-summary    — MFA coverage breakdown
GET  /api/identity/inactive-users — Users inactive 30+ days
GET  /api/devices                 — Device posture
GET  /api/backups                 — Backup job status
GET  /api/incidents               — Security incidents
POST /api/incidents/{id}/acknowledge
POST /api/incidents/{id}/resolve
GET  /api/tasks                   — Remediation tasks
POST /api/tasks                   — Create task
PATCH /api/tasks/{id}             — Update task
GET  /api/integrations/status     — Integration connection status
GET  /api/integrations/microsoft/authorize  — Start OAuth flow
GET  /api/integrations/google/authorize
GET  /health                      — Health check
```

## Connecting Microsoft 365

1. Register an app in [Azure Portal](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps)
2. Add redirect URI: `http://localhost:8000/api/integrations/microsoft/callback`
3. Grant API permissions: `User.Read.All`, `AuditLog.Read.All`, `UserAuthenticationMethod.Read.All`, `IdentityRiskyUser.Read.All`
4. Add to `.env`: `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`, `MICROSOFT_TENANT_ID`
5. Click "Connect" in Settings → Integrations

## Connecting Google Workspace

1. Create OAuth credentials in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Enable Admin SDK, Reports API
3. Add redirect URI: `http://localhost:8000/api/integrations/google/callback`
4. Add to `.env`: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
5. Click "Connect" in Settings → Integrations

## Security Score Calculation

| Control | Weight |
|---------|--------|
| MFA coverage | 30 pts |
| No critical/high incidents open | 25 pts |
| Device compliance rate | 20 pts |
| Backup health | 15 pts |
| No inactive accounts | 10 pts |

## Project Structure

```
cybersec-control-center/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Pydantic settings
│   │   ├── database.py      # SQLAlchemy async engine
│   │   ├── models/          # ORM models
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── middleware/      # Auth + logging
│   │   └── seed.py          # Demo data
│   ├── alembic/             # DB migrations
│   ├── tests/               # pytest tests
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js App Router
│   │   ├── dashboard/       # Main dashboard pages
│   │   └── settings/        # Configuration pages
│   ├── components/          # React components
│   └── lib/                 # API client + types
├── docker-compose.yml
└── .env.example
```

## Running Tests

```bash
cd backend

# Install test dependencies
python -m pip install pytest pytest-asyncio aiosqlite

# Run tests
pytest tests/ -v
```

## Production Deployment

For production:
1. Change `SECRET_KEY` to a cryptographically random value: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Change `NEXTAUTH_SECRET` similarly
3. Set `ENVIRONMENT=production`
4. Use a managed PostgreSQL service (RDS, Cloud SQL, Supabase)
5. Configure proper OAuth redirect URIs for your domain
6. Enable HTTPS (required for OAuth)
7. Remove demo data seeding from startup

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic
- **Database**: PostgreSQL 16
- **Auth**: NextAuth.js (frontend), JWT (API)
- **Scheduler**: APScheduler (background sync)
- **Container**: Docker + Docker Compose
