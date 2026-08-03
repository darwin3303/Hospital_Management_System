import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError, ConflictError, ValidationAppError
from app.features.appointments import domain
from app.features.appointments.models import Appointment
from app.features.appointments.repository import AppointmentRepository
from app.features.appointments.schemas import AppointmentCreate, AppointmentRescheduleRequest
from app.features.auth.models import User
from app.features.doctors.repository import DoctorRepository
from app.features.patients.repository import PatientRepository


class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AppointmentRepository(db)
        self.doctor_repo = DoctorRepository(db)
        self.patient_repo = PatientRepository(db)

    def book(self, payload: AppointmentCreate, actor: User) -> Appointment:
        if self.doctor_repo.get(payload.doctor_id) is None:
            raise NotFoundError("Doctor not found.", code="DOCTOR_NOT_FOUND")
        if self.patient_repo.get(payload.patient_id) is None:
            raise NotFoundError("Patient not found.", code="PATIENT_NOT_FOUND")

        # Lock this doctor's existing appointments to close the race window
        # between the overlap check and the insert (R1).
        locked_rows = self.db.scalars(
            select(Appointment).where(Appointment.doctor_id == payload.doctor_id).with_for_update()
        ).all()
        existing = [{"scheduled_at": a.scheduled_at, "duration_minutes": a.duration_minutes, "status": a.status}
                    for a in locked_rows]

        if domain.has_overlap(payload.scheduled_at, payload.duration_minutes, existing):
            raise ConflictError("This doctor already has an appointment in the selected time slot.",
                                 code="APPOINTMENT_OVERLAP")

        appt = Appointment(
            id=uuid.uuid4(), patient_id=payload.patient_id, doctor_id=payload.doctor_id,
            scheduled_at=payload.scheduled_at, duration_minutes=payload.duration_minutes,
            status="SCHEDULED", created_by=actor.id,
        )
        self.repo.create(appt)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="BOOK_APPOINTMENT", entity_type="Appointment", entity_id=str(appt.id))
        self.db.commit()
        self.db.refresh(appt)
        return appt

    def get(self, appointment_id: str) -> Appointment:
        appt = self.repo.get(appointment_id)
        if appt is None:
            raise NotFoundError("Appointment not found.", code="APPOINTMENT_NOT_FOUND")
        return appt

    def cancel(self, appointment_id: str, actor: User) -> Appointment:
        appt = self.get(appointment_id)
        if not domain.can_cancel_or_reschedule(appt.status):
            raise ConflictError("Only scheduled appointments can be cancelled.", code="INVALID_STATE_TRANSITION")
        appt.status = "CANCELLED"
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CANCEL_APPOINTMENT", entity_type="Appointment", entity_id=str(appt.id))
        self.db.commit()
        self.db.refresh(appt)
        return appt

    def reschedule(self, appointment_id: str, payload: AppointmentRescheduleRequest, actor: User) -> Appointment:
        appt = self.get(appointment_id)
        if not domain.can_cancel_or_reschedule(appt.status):
            raise ConflictError("Only scheduled appointments can be rescheduled.", code="INVALID_STATE_TRANSITION")

        duration = payload.duration_minutes or appt.duration_minutes
        locked_rows = self.db.scalars(
            select(Appointment).where(Appointment.doctor_id == appt.doctor_id,
                                       Appointment.id != appt.id).with_for_update()
        ).all()
        existing = [{"scheduled_at": a.scheduled_at, "duration_minutes": a.duration_minutes, "status": a.status}
                    for a in locked_rows]
        if domain.has_overlap(payload.scheduled_at, duration, existing):
            raise ConflictError("This doctor already has an appointment in the selected time slot.",
                                 code="APPOINTMENT_OVERLAP")

        appt.scheduled_at = payload.scheduled_at
        appt.duration_minutes = duration
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="RESCHEDULE_APPOINTMENT", entity_type="Appointment", entity_id=str(appt.id))
        self.db.commit()
        self.db.refresh(appt)
        return appt

    def complete(self, appointment_id: str, actor: User) -> Appointment:
        appt = self.get(appointment_id)
        from app.features.emr.repository import EmrRepository
        has_record = EmrRepository(self.db).get_by_appointment(appointment_id) is not None

        if not domain.can_complete(appt.status, has_record):
            if appt.status != "SCHEDULED":
                raise ConflictError("Only scheduled appointments can be completed.", code="INVALID_STATE_TRANSITION")
            raise ValidationAppError("A medical record must be created before completing this appointment.",
                                      code="MEDICAL_RECORD_REQUIRED")

        appt.status = "COMPLETED"
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="COMPLETE_APPOINTMENT", entity_type="Appointment", entity_id=str(appt.id))
        self.db.commit()
        self.db.refresh(appt)
        return appt

    def mark_no_show(self, appointment_id: str, actor: User) -> Appointment:
        appt = self.get(appointment_id)
        if not domain.can_mark_no_show(appt.status):
            raise ConflictError("Only scheduled appointments can be marked no-show.", code="INVALID_STATE_TRANSITION")
        appt.status = "NO_SHOW"
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="NO_SHOW_APPOINTMENT", entity_type="Appointment", entity_id=str(appt.id))
        self.db.commit()
        self.db.refresh(appt)
        return appt

    def list_paginated(self, page: int, page_size: int, doctor_id: str | None = None,
                        patient_id: str | None = None, status: str | None = None):
        return self.repo.list_paginated(page, page_size, doctor_id, patient_id, status)

    def doctor_queue(self, doctor_id: str, status: str | None = "SCHEDULED") -> list[Appointment]:
        return self.repo.list_for_doctor(doctor_id, status)
