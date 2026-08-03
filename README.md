[README.md](https://github.com/user-attachments/files/30678324/README.md)
# Hospital Management System

A full-stack Hospital Management System built with FastAPI (backend) and
React + Ant Design (frontend), covering the complete patient journey across
7 roles: Admin, Receptionist, Doctor, Nurse, Laboratory Staff, Pharmacist,
and Accountant.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic |
| Frontend | React, Vite, TypeScript, Ant Design, TanStack Query |
| Auth | JWT access tokens + httpOnly-cookie refresh tokens (server-revocable) |
| Architecture | Feature-Based Clean Architecture (see `backend/docs/architecture.md`) |

## Project structure

```
hms/
├── backend/
│   ├── app/
│   │   ├── core/           # shared infra: auth, RBAC, errors, audit, config
│   │   └── features/       # one folder per module (auth, patients, billing, etc.)
│   ├── alembic/             # database migrations
│   ├── scripts/              # seed_admin, seed_demo_data, reset_db, check_health
│   ├── docs/                 # architecture.md, database.md, api.md, adr/
│   ├── tests/
│   ├── requirements.txt
│   └── .env                  # NOT committed -- create locally, see below
│
└── frontend/
    ├── src/
    │   ├── api/              # one file per feature, calls the backend
    │   ├── pages/             # one folder per role
    │   ├── components/
    │   ├── theme/              # colour palette + Ant Design theme config
    │   └── context/            # auth state
    └── package.json
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ (tested on 18)

## 1. Backend setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend\.env` (this file is never committed to version control):

```
ENV=development
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/hms_db
JWT_SECRET=<generate with the command below>
REFRESH_SECRET=<generate with the command below>
ACCESS_TOKEN_TTL_MINUTES=30
REFRESH_TOKEN_TTL_DAYS=7
CLIENT_ORIGIN=http://localhost:5173
BCRYPT_ROUNDS=12
```

Generate two different random secrets locally:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Create the databases:
```powershell
& "C:\Program Files\PostgreSQL\<version>\bin\psql.exe" -U postgres
```
```sql
CREATE DATABASE hms_db;
CREATE DATABASE hms_test_db;
\q
```

Run migrations:
```powershell
alembic upgrade head
```

Seed initial data:
```powershell
python scripts/seed_admin.py
python scripts/seed_demo_data.py
```

Verify everything is wired correctly:
```powershell
python scripts/check_health.py
```

Start the API:
```powershell
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 2. Frontend setup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## 3. Default logins (after running seed_demo_data.py)

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@1234` |
| Doctor | `drnadeesha` | `Doctor@1234` |
| Receptionist | `receptionist1` | `Reception@1234` |
| Lab Staff | `labstaff1` | `LabStaff@1234` |
| Pharmacist | `pharmacist1` | `Pharma@1234` |
| Accountant | `accountant1` | `Account@1234` |

Change these before any real deployment.

## Running tests

```powershell
cd backend
pytest tests/unit/ -v          # pure domain logic, no DB required
pytest tests/ -v                 # full suite, needs hms_test_db reachable
```

## Useful backend scripts

| Script | Purpose |
|---|---|
| `scripts/seed_admin.py` | Creates the first Admin user (idempotent) |
| `scripts/seed_demo_data.py` | Seeds a full demo dataset: department, doctor, patient, appointment, medicine |
| `scripts/reset_db.py` | Drops and recreates all tables (local dev only) |
| `scripts/check_health.py` | One command to verify DB connection, migrations, admin user, and API reachability before a demo |

## Documentation

- `backend/docs/architecture.md` — architecture principles, module boundaries
- `backend/docs/database.md` — schema, key design decisions, constraints
- `backend/docs/api.md` — full endpoint list (regeneratable from the live route table)
- `backend/docs/adr/` — architecture decision records, one file per decision

## Known limitations

- Document upload has a backend endpoint but no dedicated frontend page yet (usable via Swagger)
- Inpatient admission/discharge has a backend endpoint but no dedicated frontend page yet (usable via Swagger)
- Medical record amendments have a backend endpoint but no dedicated frontend page yet
- Doctor working-hours editing after initial creation has no frontend page yet
- No automated frontend tests yet
- Production bundle isn't code-split (fine for local/demo use)

## Troubleshooting

**`psql` not recognized** — use the full path:
```powershell
& "C:\Program Files\PostgreSQL\<version>\bin\psql.exe" -U postgres
```

**`password authentication failed`** — the password in `DATABASE_URL` inside `.env` doesn't match your actual Postgres password. Update it there.

**`ModuleNotFoundError`** — your virtual environment isn't active. Run `venv\Scripts\activate` first (prompt should show `(venv)`).

**Frontend shows stale/no data after an action** — check the access token hasn't expired (default 30 min); log in again.

**Any 500 error** — check the terminal running `uvicorn` for the full traceback; the standard error envelope (`{success, code, message, details}`) covers expected business-rule failures, but unexpected exceptions still surface as a generic `INTERNAL_ERROR` with full detail in the server log.
