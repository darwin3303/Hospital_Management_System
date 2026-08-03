from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.pagination import page_params, paginate_meta, PageParams
from app.core.roles import Role
from app.features.auth.models import User
from app.features.appointments.schemas import AppointmentCreate, AppointmentRescheduleRequest, AppointmentOut
from app.features.appointments.service import AppointmentService
from app.features.doctors.repository import DoctorRepository
from app.core.errors import ForbiddenError

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def book_appointment(payload: AppointmentCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    appt = AppointmentService(db).book(payload, current_user)
    return {"success": True, "data": AppointmentOut.model_validate(appt)}


@router.get("")
def list_appointments(db: Session = Depends(get_db), pagination: PageParams = Depends(page_params),
                       doctor_id: str | None = None, patient_id: str | None = None,
                       status: str | None = None, current_user: User = Depends(get_current_user)):
    # Doctor Queue support: "me" resolves to the caller's own doctor profile,
    # scoping the query server-side rather than trusting a client-supplied doctor_id.
    if doctor_id == "me":
        from sqlalchemy import select
        from app.features.staff.models import Employee
        from app.features.doctors.models import Doctor
        emp = db.scalar(select(Employee).where(Employee.user_id == current_user.id))
        if emp is None:
            raise ForbiddenError("No doctor profile linked to this account.", code="NOT_A_DOCTOR")
        doc = db.scalar(select(Doctor).where(Doctor.employee_id == emp.id))
        if doc is None:
            raise ForbiddenError("No doctor profile linked to this account.", code="NOT_A_DOCTOR")
        doctor_id = str(doc.id)

    items, total = AppointmentService(db).list_paginated(
        pagination.page, pagination.page_size, doctor_id, patient_id, status
    )
    return {"success": True, "data": [AppointmentOut.model_validate(a) for a in items],
            "meta": paginate_meta(pagination.page, pagination.page_size, total)}


@router.put("/{appointment_id}/cancel", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    appt = AppointmentService(db).cancel(appointment_id, current_user)
    return {"success": True, "data": AppointmentOut.model_validate(appt)}


@router.put("/{appointment_id}/reschedule", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def reschedule_appointment(appointment_id: str, payload: AppointmentRescheduleRequest,
                            db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appt = AppointmentService(db).reschedule(appointment_id, payload, current_user)
    return {"success": True, "data": AppointmentOut.model_validate(appt)}


@router.put("/{appointment_id}/complete", dependencies=[Depends(require_role(Role.DOCTOR))])
def complete_appointment(appointment_id: str, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    appt = AppointmentService(db).complete(appointment_id, current_user)
    return {"success": True, "data": AppointmentOut.model_validate(appt)}


@router.put("/{appointment_id}/no-show", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def no_show_appointment(appointment_id: str, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    appt = AppointmentService(db).mark_no_show(appointment_id, current_user)
    return {"success": True, "data": AppointmentOut.model_validate(appt)}
