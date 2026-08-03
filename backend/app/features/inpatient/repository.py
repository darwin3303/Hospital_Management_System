from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.inpatient.models import Admission


class InpatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, admission: Admission) -> Admission:
        self.db.add(admission)
        self.db.flush()
        return admission

    def get(self, admission_id: str) -> Admission | None:
        return self.db.get(Admission, admission_id)

    def get_active_for_patient(self, patient_id: str) -> Admission | None:
        return self.db.scalar(
            select(Admission).where(Admission.patient_id == patient_id, Admission.status == "ACTIVE")
        )
