from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.roles import Role
from app.features.auth.models import User
from app.features.doctors.schemas import DoctorCreate, DoctorOut, AvailabilitySlot, AvailabilityOut
from app.features.doctors.service import DoctorService

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("", dependencies=[Depends(require_role(Role.ADMIN))])
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    doctor = DoctorService(db).create_doctor(payload, current_user)
    return {"success": True, "data": DoctorOut.model_validate(doctor)}


@router.get("")
def list_doctors(db: Session = Depends(get_db), _=Depends(get_current_user)):
    doctors = DoctorService(db).list_doctors()
    return {"success": True, "data": [DoctorOut.model_validate(d) for d in doctors]}


@router.get("/{doctor_id}")
def get_doctor(doctor_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    doctor = DoctorService(db).get(doctor_id)
    return {"success": True, "data": DoctorOut.model_validate(doctor)}


@router.post("/{doctor_id}/availability", dependencies=[Depends(require_role(Role.ADMIN))])
def add_availability(doctor_id: str, payload: AvailabilitySlot, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    slot = DoctorService(db).add_availability(doctor_id, payload, current_user)
    return {"success": True, "data": AvailabilityOut.model_validate(slot)}


@router.get("/{doctor_id}/availability")
def list_availability(doctor_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    slots = DoctorService(db).list_availability(doctor_id)
    return {"success": True, "data": [AvailabilityOut.model_validate(s) for s in slots]}
