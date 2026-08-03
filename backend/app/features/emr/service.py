import uuid

from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError, ConflictError, ForbiddenError
from app.features.auth.models import User
from app.features.emr import domain
from app.features.emr.models import MedicalRecord, MedicalRecordAmendment, Prescription, PrescriptionItem
from app.features.emr.repository import EmrRepository
from app.features.emr.schemas import MedicalRecordCreate, PrescriptionCreate
from app.features.appointments.repository import AppointmentRepository


class EmrService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EmrRepository(db)
        self.appt_repo = AppointmentRepository(db)

    def create_record(self, payload: MedicalRecordCreate, doctor_id: str, actor: User) -> MedicalRecord:
        appt = self.appt_repo.get(payload.appointment_id)
        if appt is None:
            raise NotFoundError("Appointment not found.", code="APPOINTMENT_NOT_FOUND")

        if not domain.can_document(appt.status):
            raise ConflictError("Documentation can only be added while the appointment is scheduled.",
                                 code="INVALID_DOCUMENTATION_STATE")

        if self.repo.get_by_appointment(payload.appointment_id) is not None:
            raise ConflictError("A medical record already exists for this appointment.",
                                 code="MEDICAL_RECORD_ALREADY_EXISTS")

        record = MedicalRecord(
            id=uuid.uuid4(), appointment_id=payload.appointment_id, doctor_id=doctor_id,
            patient_id=appt.patient_id, diagnosis=payload.diagnosis, notes=payload.notes,
        )
        self.repo.create_record(record)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CREATE_MEDICAL_RECORD", entity_type="MedicalRecord", entity_id=str(record.id))
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_appointment(self, appointment_id: str, requesting_doctor_id: str | None = None) -> MedicalRecord:
        record = self.repo.get_by_appointment(appointment_id)
        if record is None:
            raise NotFoundError("Medical record not found.", code="MEDICAL_RECORD_NOT_FOUND")
        if requesting_doctor_id and not domain.owns_record(str(record.doctor_id), requesting_doctor_id):
            raise ForbiddenError("You may only view your own patients' records.", code="RECORD_NOT_OWNED")
        return record

    def get_history(self, patient_id: str) -> list[MedicalRecord]:
        # Nurse role reads this too, but read-only and not doctor-ownership-scoped
        # since Nurse has no "own patients" concept in this system.
        return self.repo.list_history_for_patient(patient_id)

    def add_amendment(self, record_id: str, amended_text: str, actor: User) -> MedicalRecordAmendment:
        record = self.repo.get(record_id)
        if record is None:
            raise NotFoundError("Medical record not found.", code="MEDICAL_RECORD_NOT_FOUND")
        amendment = MedicalRecordAmendment(
            id=uuid.uuid4(), medical_record_id=record_id, amended_text=amended_text, amended_by=actor.id,
        )
        self.repo.add_amendment(amendment)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="AMEND_MEDICAL_RECORD", entity_type="MedicalRecord", entity_id=str(record_id))
        self.db.commit()
        self.db.refresh(amendment)
        return amendment

    def create_prescription(self, record_id: str, payload: PrescriptionCreate, actor: User) -> Prescription:
        record = self.repo.get(record_id)
        if record is None:
            raise NotFoundError("Medical record not found.", code="MEDICAL_RECORD_NOT_FOUND")

        prescription = Prescription(id=uuid.uuid4(), medical_record_id=record_id)
        self.repo.create_prescription(prescription)

        for item in payload.items:
            self.repo.add_prescription_item(PrescriptionItem(
                id=uuid.uuid4(), prescription_id=prescription.id, medicine_id=item.medicine_id,
                quantity=item.quantity, dosage_instructions=item.dosage_instructions, status="PENDING",
            ))

        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CREATE_PRESCRIPTION", entity_type="Prescription", entity_id=str(prescription.id))
        self.db.commit()
        self.db.refresh(prescription)
        return prescription
