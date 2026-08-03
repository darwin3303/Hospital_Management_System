from sqlalchemy import select
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.errors import ForbiddenError
from app.core.roles import Role
from app.features.auth.models import User
from app.features.emr.schemas import (
    MedicalRecordCreate, MedicalRecordOut, AmendmentCreate, AmendmentOut,
    PrescriptionCreate, PrescriptionOut, PrescriptionItemOut,
)
from app.features.emr.service import EmrService

router = APIRouter(prefix="/medical-records", tags=["emr"])


def _resolve_doctor_id(db: Session, current_user: User) -> str:
    from app.features.staff.models import Employee
    from app.features.doctors.models import Doctor
    emp = db.scalar(select(Employee).where(Employee.user_id == current_user.id))
    if emp is None:
        raise ForbiddenError("No doctor profile linked to this account.", code="NOT_A_DOCTOR")
    doc = db.scalar(select(Doctor).where(Doctor.employee_id == emp.id))
    if doc is None:
        raise ForbiddenError("No doctor profile linked to this account.", code="NOT_A_DOCTOR")
    return str(doc.id)


@router.post("", dependencies=[Depends(require_role(Role.DOCTOR))])
def create_medical_record(payload: MedicalRecordCreate, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    doctor_id = _resolve_doctor_id(db, current_user)
    record = EmrService(db).create_record(payload, doctor_id, current_user)
    return {"success": True, "data": MedicalRecordOut.model_validate(record)}


@router.get("/appointment/{appointment_id}",
            dependencies=[Depends(require_role(Role.DOCTOR, Role.NURSE, Role.ADMIN))])
def get_by_appointment(appointment_id: str, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    requesting_doctor_id = None
    if current_user.role == Role.DOCTOR.value:
        requesting_doctor_id = _resolve_doctor_id(db, current_user)
    record = EmrService(db).get_by_appointment(appointment_id, requesting_doctor_id)
    return {"success": True, "data": MedicalRecordOut.model_validate(record)}


@router.get("/patient/{patient_id}/history",
            dependencies=[Depends(require_role(Role.DOCTOR, Role.NURSE, Role.ADMIN))])
def get_history(patient_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    records = EmrService(db).get_history(patient_id)
    return {"success": True, "data": [MedicalRecordOut.model_validate(r) for r in records]}


@router.post("/{record_id}/amendments", dependencies=[Depends(require_role(Role.DOCTOR))])
def add_amendment(record_id: str, payload: AmendmentCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    amendment = EmrService(db).add_amendment(record_id, payload.amended_text, current_user)
    return {"success": True, "data": AmendmentOut.model_validate(amendment)}


@router.post("/{record_id}/prescriptions", dependencies=[Depends(require_role(Role.DOCTOR))])
def create_prescription(record_id: str, payload: PrescriptionCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    service = EmrService(db)
    prescription = service.create_prescription(record_id, payload, current_user)
    items = service.repo.list_items_for_prescription(str(prescription.id))
    data = PrescriptionOut.model_validate(prescription)
    data.items = [PrescriptionItemOut.model_validate(i) for i in items]
    return {"success": True, "data": data}
