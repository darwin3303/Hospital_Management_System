from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.laboratory.models import LabRequest


class LaboratoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, req: LabRequest) -> LabRequest:
        self.db.add(req)
        self.db.flush()
        return req

    def get(self, request_id: str) -> LabRequest | None:
        return self.db.get(LabRequest, request_id)

    def list_by_status(self, status: str | None) -> list[LabRequest]:
        stmt = select(LabRequest)
        if status:
            stmt = stmt.where(LabRequest.status == status)
        return list(self.db.scalars(stmt.order_by(LabRequest.requested_at)).all())

    def list_for_medical_record(self, medical_record_id: str) -> list[LabRequest]:
        return list(self.db.scalars(
            select(LabRequest).where(LabRequest.medical_record_id == medical_record_id)
        ).all())
