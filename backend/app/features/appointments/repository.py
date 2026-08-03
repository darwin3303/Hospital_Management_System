from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.features.appointments.models import Appointment


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, appt: Appointment) -> Appointment:
        self.db.add(appt)
        self.db.flush()
        return appt

    def get(self, appointment_id: str) -> Appointment | None:
        return self.db.get(Appointment, appointment_id)

    def list_for_doctor(self, doctor_id: str, status: str | None = None) -> list[Appointment]:
        stmt = select(Appointment).where(Appointment.doctor_id == doctor_id)
        if status:
            stmt = stmt.where(Appointment.status == status)
        return list(self.db.scalars(stmt.order_by(Appointment.scheduled_at)).all())

    def list_paginated(self, page: int, page_size: int, doctor_id: str | None = None,
                        patient_id: str | None = None, status: str | None = None) -> tuple[list[Appointment], int]:
        stmt = select(Appointment)
        if doctor_id:
            stmt = stmt.where(Appointment.doctor_id == doctor_id)
        if patient_id:
            stmt = stmt.where(Appointment.patient_id == patient_id)
        if status:
            stmt = stmt.where(Appointment.status == status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        items = self.db.scalars(
            stmt.order_by(Appointment.scheduled_at.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
        return list(items), total
