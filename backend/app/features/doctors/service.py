import uuid

from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError, ConflictError, ForbiddenError
from app.features.auth.models import User
from app.features.doctors import domain
from app.features.doctors.models import Doctor, DoctorAvailability
from app.features.doctors.repository import DoctorRepository
from app.features.doctors.schemas import DoctorCreate
from app.features.staff.repository import StaffRepository


class DoctorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DoctorRepository(db)
        self.staff_repo = StaffRepository(db)  # read-only cross-feature read, via repo not raw SQL

    def create_doctor(self, payload: DoctorCreate, actor: User) -> Doctor:
        employee = self.staff_repo.get_employee(payload.employee_id)
        if employee is None:
            raise NotFoundError("Employee not found.", code="EMPLOYEE_NOT_FOUND")
        if self.repo.get_by_employee(payload.employee_id) is not None:
            raise ConflictError("This employee is already registered as a doctor.", code="DOCTOR_ALREADY_EXISTS")

        # R7: employee's linked user must have role DOCTOR
        employee_role = None
        if employee.user_id:
            from app.features.auth.repository import AuthRepository
            linked_user = AuthRepository(self.db).get_by_id(str(employee.user_id))
            employee_role = linked_user.role if linked_user else None

        if not domain.can_link_doctor(employee_role):
            raise ForbiddenError(
                "Doctor profile can only be linked to an employee whose account role is DOCTOR.",
                code="INVALID_DOCTOR_LINKAGE",
            )

        doctor = Doctor(id=uuid.uuid4(), employee_id=payload.employee_id,
                         specialty=payload.specialty, consultation_fee=payload.consultation_fee)
        self.repo.create_doctor(doctor)

        for slot in payload.availability:
            self.repo.add_availability(DoctorAvailability(
                id=uuid.uuid4(), doctor_id=doctor.id, day_of_week=slot.day_of_week,
                start_time=slot.start_time, end_time=slot.end_time,
            ))

        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CREATE_DOCTOR", entity_type="Doctor", entity_id=str(doctor.id))
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def get(self, doctor_id: str) -> Doctor:
        doctor = self.repo.get(doctor_id)
        if doctor is None:
            raise NotFoundError("Doctor not found.", code="DOCTOR_NOT_FOUND")
        return doctor

    def list_doctors(self) -> list[Doctor]:
        return self.repo.list_doctors()

    def list_availability(self, doctor_id: str) -> list[DoctorAvailability]:
        return self.repo.list_availability(doctor_id)

    def add_availability(self, doctor_id: str, slot_payload, actor: User) -> DoctorAvailability:
        if self.repo.get(doctor_id) is None:
            raise NotFoundError("Doctor not found.", code="DOCTOR_NOT_FOUND")
        slot = DoctorAvailability(id=uuid.uuid4(), doctor_id=doctor_id, day_of_week=slot_payload.day_of_week,
                                   start_time=slot_payload.start_time, end_time=slot_payload.end_time)
        self.repo.add_availability(slot)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="ADD_AVAILABILITY", entity_type="Doctor", entity_id=str(doctor_id))
        self.db.commit()
        self.db.refresh(slot)
        return slot
