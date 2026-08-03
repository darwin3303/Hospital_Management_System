from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.emr.models import MedicalRecord, MedicalRecordAmendment, Prescription, PrescriptionItem


class EmrRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_record(self, record: MedicalRecord) -> MedicalRecord:
        self.db.add(record)
        self.db.flush()
        return record

    def get(self, record_id: str) -> MedicalRecord | None:
        return self.db.get(MedicalRecord, record_id)

    def get_by_appointment(self, appointment_id: str) -> MedicalRecord | None:
        return self.db.scalar(select(MedicalRecord).where(MedicalRecord.appointment_id == appointment_id))

    def list_history_for_patient(self, patient_id: str) -> list[MedicalRecord]:
        return list(self.db.scalars(
            select(MedicalRecord).where(MedicalRecord.patient_id == patient_id)
            .order_by(MedicalRecord.created_at.desc())
        ).all())

    def add_amendment(self, amendment: MedicalRecordAmendment) -> MedicalRecordAmendment:
        self.db.add(amendment)
        self.db.flush()
        return amendment

    def create_prescription(self, prescription: Prescription) -> Prescription:
        self.db.add(prescription)
        self.db.flush()
        return prescription

    def add_prescription_item(self, item: PrescriptionItem) -> PrescriptionItem:
        self.db.add(item)
        self.db.flush()
        return item

    def get_prescription_item(self, item_id: str) -> PrescriptionItem | None:
        return self.db.get(PrescriptionItem, item_id)

    def list_pending_prescription_items(self) -> list[PrescriptionItem]:
        return list(self.db.scalars(
            select(PrescriptionItem).where(PrescriptionItem.status == "PENDING")
        ).all())

    def list_items_for_prescription(self, prescription_id: str) -> list[PrescriptionItem]:
        return list(self.db.scalars(
            select(PrescriptionItem).where(PrescriptionItem.prescription_id == prescription_id)
        ).all())
