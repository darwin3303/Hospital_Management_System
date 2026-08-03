import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.request_context import RequestIDMiddleware

from app.features.auth.router import router as auth_router, users_router
from app.features.staff.router import router as staff_router
from app.features.doctors.router import router as doctors_router
from app.features.patients.router import router as patients_router
from app.features.appointments.router import router as appointments_router
from app.features.emr.router import router as emr_router
from app.features.laboratory.router import router as laboratory_router
from app.features.pharmacy.router import router as pharmacy_router
from app.features.billing.router import router as billing_router
from app.features.inpatient.router import router as inpatient_router
from app.features.reports.router import router as reports_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="Hospital Management System API", version="1.0.0")

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_ORIGIN],
    allow_credentials=True,   # required for the httpOnly refresh cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(staff_router, prefix=API_PREFIX)
app.include_router(doctors_router, prefix=API_PREFIX)
app.include_router(patients_router, prefix=API_PREFIX)
app.include_router(appointments_router, prefix=API_PREFIX)
app.include_router(emr_router, prefix=API_PREFIX)
app.include_router(laboratory_router, prefix=API_PREFIX)
app.include_router(pharmacy_router, prefix=API_PREFIX)
app.include_router(billing_router, prefix=API_PREFIX)
app.include_router(inpatient_router, prefix=API_PREFIX)
app.include_router(reports_router, prefix=API_PREFIX)


@app.get("/health")
def health():
    return {"success": True, "data": {"status": "ok"}}


@app.get("/health/db")
def health_db():
    from app.core.database import SessionLocal
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"success": True, "data": {"status": "ok"}}
    except Exception as exc:
        return {"success": False, "code": "DB_UNAVAILABLE", "message": str(exc), "details": {}}
