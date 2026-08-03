import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError, ConflictError, ValidationAppError
from app.features.auth.models import User
from app.features.emr.repository import EmrRepository
from app.features.inpatient import domain
from app.features.inpatient.models import Admission
from app.features.inpatient.repository import InpatientRepository
from app.features.inpatient.schemas import AdmissionCreate
from app.features.patients.repository import PatientRepository


class InpatientService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InpatientRepository(db)
        self.patient_repo = PatientRepository(db)
        self.emr_repo = EmrRepository(db)

    def admit(self, payload: AdmissionCreate, actor: User) -> Admission:
        if self.patient_repo.get(payload.patient_id) is None:
            raise NotFoundError("Patient not found.", code="PATIENT_NOT_FOUND")

        # R18: one active admission per patient -- app-level check plus the
        # partial unique index as the database-level backstop against races.
        if self.repo.get_active_for_patient(payload.patient_id) is not None:
            raise ConflictError("This patient already has an active admission.",
                                 code="ACTIVE_ADMISSION_EXISTS")

        admission = Admission(
            id=uuid.uuid4(), patient_id=payload.patient_id, appointment_id=payload.appointment_id,
            ward=payload.ward, bed_number=payload.bed_number, status="ACTIVE",
        )
        try:
            self.repo.create(admission)
        except IntegrityError:
            raise ConflictError("This patient already has an active admission.",
                                 code="ACTIVE_ADMISSION_EXISTS")

        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="ADMIT_PATIENT", entity_type="Admission", entity_id=str(admission.id))
        self.db.commit()
        self.db.refresh(admission)
        return admission

    def get(self, admission_id: str) -> Admission:
        admission = self.repo.get(admission_id)
        if admission is None:
            raise NotFoundError("Admission not found.", code="ADMISSION_NOT_FOUND")
        return admission

    def discharge(self, admission_id: str, discharge_medical_record_id: str, actor: User) -> Admission:
        admission = self.get(admission_id)
        record = self.emr_repo.get(discharge_medical_record_id)
        has_record = record is not None

        if not domain.can_discharge(admission.status, has_record):
            if admission.status != "ACTIVE":
                raise ConflictError("Only an active admission can be discharged.", code="INVALID_STATE_TRANSITION")
            raise ValidationAppError("A valid medical record is required as the discharge summary.",
                                      code="DISCHARGE_SUMMARY_REQUIRED")

        admission.status = "DISCHARGED"
        admission.discharge_medical_record_id = discharge_medical_record_id
        admission.discharged_at = datetime.now(timezone.utc)

        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="DISCHARGE_PATIENT", entity_type="Admission", entity_id=str(admission.id))
        self.db.commit()
        self.db.refresh(admission)
        return admission
