# Hospital Management System — Backend

FastAPI + SQLAlchemy 2.0 + PostgreSQL, Feature-Based Clean Architecture.

## 1. Install

```bash
cd hms-backend
python -m venv venv
venv\Scripts\activate        # Windows PowerShell
pip install -r requirements.txt
```

Copy the env file and fill in real secrets:

```bash
copy .env.example .env
```

Edit `.env` — at minimum set `DATABASE_URL` to your local Postgres, and set
`JWT_SECRET` / `REFRESH_SECRET` to random strings.

## 2. Create the database

In PowerShell, using `psql` (or pgAdmin):

```sql
CREATE DATABASE hms_db;
CREATE DATABASE hms_test_db;   -- separate DB for the test suite
```

## 3. Run migrations

Generate the first migration from the models (autogenerate compares your
models against the current empty database and writes the matching SQL):

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Every time you change a model afterward: repeat those two commands with a
new message. Always **read the generated migration file** before running
upgrade — autogenerate is a draft, not a guarantee, especially for
constraints like the partial unique index on admissions.

## 4. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs
Health check: http://localhost:8000/health

## 5. Run the tests

Unit tests (pure domain logic, no database needed):

```bash
pytest tests/unit/ -v
```

Integration/e2e tests (need `hms_test_db` to exist and be reachable via the
`DATABASE_URL` in your environment — conftest.py creates and tears down
tables automatically per test using a transaction rollback, so tests never
leave residue):

```bash
pytest tests/ -v
```

Run one feature's tests only:

```bash
pytest tests/integration/test_appointments.py -v
```

## 6. Manual/exploratory testing via Swagger

1. Go to `/docs`
2. First create an Admin user directly in the database (chicken-and-egg: the
   `/users` endpoint itself requires an Admin token) — see seed script below
   — or temporarily relax the `require_role` on `POST /users` while seeding,
   then restore it.
3. `POST /auth/login` with that admin's credentials → copy the `access_token`
4. Click "Authorize" in Swagger, paste `Bearer <access_token>`
5. Now every other endpoint is callable in-browser, with RBAC enforced exactly
   as the API would enforce it for a real frontend.

### Seeding the first Admin user

Simplest approach — a one-off script:

```python
# seed_admin.py — run once: python seed_admin.py
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.features.auth.models import User
import uuid

db = SessionLocal()
db.add(User(id=uuid.uuid4(), username="admin", password_hash=hash_password("Admin@1234"),
            role="ADMIN", is_active=True))
db.commit()
print("Admin created: admin / Admin@1234")
```

## 7. Testing a full workflow manually (PowerShell)

```powershell
# Login
$login = Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/login -Method Post `
  -ContentType "application/json" -Body '{"username":"admin","password":"Admin@1234"}'
$token = $login.data.access_token
$headers = @{ Authorization = "Bearer $token" }

# Create a department
Invoke-RestMethod -Uri http://localhost:8000/api/v1/staff/departments -Method Post `
  -Headers $headers -ContentType "application/json" -Body '{"name":"General Medicine"}'
```

Repeat this pattern per module, following the dependency order: auth → staff
→ doctors → patients → appointments → emr → laboratory/pharmacy → billing →
inpatient → reports. Each module's Swagger tag groups its endpoints for easy
manual walkthroughs.

## Project layout

See `app/features/<name>/` for each of the 11 business features
(domain / schemas / service / repository / models / router), and `app/core/`
for shared infrastructure (auth, RBAC, errors, audit, pagination).
