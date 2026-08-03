from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.doctors.models import Doctor, DoctorAvailability


class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_doctor(self, doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        self.db.flush()
        return doctor

    def get(self, doctor_id: str) -> Doctor | None:
        return self.db.get(Doctor, doctor_id)

    def get_by_employee(self, employee_id: str) -> Doctor | None:
        return self.db.scalar(select(Doctor).where(Doctor.employee_id == employee_id))

    def list_doctors(self) -> list[Doctor]:
        return list(self.db.scalars(select(Doctor)).all())

    def add_availability(self, slot: DoctorAvailability) -> DoctorAvailability:
        self.db.add(slot)
        self.db.flush()
        return slot

    def list_availability(self, doctor_id: str) -> list[DoctorAvailability]:
        return list(self.db.scalars(
            select(DoctorAvailability).where(DoctorAvailability.doctor_id == doctor_id)
        ).all())
