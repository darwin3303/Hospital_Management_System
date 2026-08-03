from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.roles import Role
from app.features.reports.service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/patients", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def patients_report(db: Session = Depends(get_db)):
    items = ReportsService(db).patients_report()
    return {"success": True, "data": [
        {"id": str(p.id), "first_name": p.first_name, "last_name": p.last_name, "phone": p.phone}
        for p in items
    ]}


@router.get("/appointments", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def appointments_report(status: str | None = None, db: Session = Depends(get_db)):
    items = ReportsService(db).appointments_report(status)
    return {"success": True, "data": [
        {"id": str(a.id), "status": a.status, "scheduled_at": a.scheduled_at.isoformat()} for a in items
    ]}


@router.get("/revenue", dependencies=[Depends(require_role(Role.ADMIN, Role.ACCOUNTANT))])
def revenue_report(db: Session = Depends(get_db)):
    return {"success": True, "data": ReportsService(db).revenue_report()}


@router.get("/pharmacy", dependencies=[Depends(require_role(Role.ADMIN, Role.PHARMACIST))])
def pharmacy_report(db: Session = Depends(get_db)):
    items = ReportsService(db).pharmacy_report()
    return {"success": True, "data": [
        {"medicine_name": m.name, "quantity_in_stock": m.quantity_in_stock} for m in items
    ]}


@router.get("/laboratory", dependencies=[Depends(require_role(Role.ADMIN, Role.LAB_STAFF))])
def laboratory_report(status: str | None = None, db: Session = Depends(get_db)):
    items = ReportsService(db).laboratory_report(status)
    return {"success": True, "data": [{"test_name": l.test_name, "status": l.status} for l in items]}


@router.get("/staff", dependencies=[Depends(require_role(Role.ADMIN))])
def staff_report(db: Session = Depends(get_db)):
    items = ReportsService(db).staff_report()
    return {"success": True, "data": [
        {"employee_id": str(e.id), "first_name": e.first_name, "last_name": e.last_name,
         "department_id": str(e.department_id)} for e in items
    ]}


@router.get("/overview", dependencies=[Depends(require_role(Role.ADMIN))])
def overview(db: Session = Depends(get_db)):
    return {"success": True, "data": ReportsService(db).overview()}
