import uuid

from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError, ConflictError
from app.features.auth.models import User
from app.features.emr.repository import EmrRepository
from app.features.laboratory import domain
from app.features.laboratory.models import LabRequest
from app.features.laboratory.repository import LaboratoryRepository
from app.features.laboratory.schemas import LabRequestCreate


class LaboratoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LaboratoryRepository(db)
        self.emr_repo = EmrRepository(db)

    def create_request(self, payload: LabRequestCreate, actor: User) -> LabRequest:
        # R8: requires an existing medical record
        if self.emr_repo.get(payload.medical_record_id) is None:
            raise NotFoundError("Medical record not found.", code="MEDICAL_RECORD_NOT_FOUND")

        req = LabRequest(id=uuid.uuid4(), medical_record_id=payload.medical_record_id,
                          test_name=payload.test_name, status="REQUESTED")
        self.repo.create(req)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CREATE_LAB_REQUEST", entity_type="LabRequest", entity_id=str(req.id))
        self.db.commit()
        self.db.refresh(req)
        return req

    def _transition(self, request_id: str, target_status: str, actor: User, result_data: str | None = None) -> LabRequest:
        req = self.repo.get(request_id)
        if req is None:
            raise NotFoundError("Lab request not found.", code="LAB_REQUEST_NOT_FOUND")
        if not domain.can_transition(req.status, target_status):
            raise ConflictError(f"Cannot move a lab request from {req.status} to {target_status}.",
                                 code="INVALID_STATE_TRANSITION")
        req.status = target_status
        if result_data is not None:
            req.result_data = result_data
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action=f"LAB_REQUEST_{target_status}", entity_type="LabRequest", entity_id=str(req.id))
        self.db.commit()
        self.db.refresh(req)
        return req

    def collect_sample(self, request_id: str, actor: User) -> LabRequest:
        return self._transition(request_id, "SAMPLE_COLLECTED", actor)

    def enter_result(self, request_id: str, result_data: str, actor: User) -> LabRequest:
        return self._transition(request_id, "RESULT_ENTERED", actor, result_data)

    def generate_report(self, request_id: str, actor: User) -> LabRequest:
        return self._transition(request_id, "REPORT_GENERATED", actor)

    def list_by_status(self, status: str | None) -> list[LabRequest]:
        return self.repo.list_by_status(status)

    def list_for_medical_record(self, medical_record_id: str) -> list[LabRequest]:
        return self.repo.list_for_medical_record(medical_record_id)
