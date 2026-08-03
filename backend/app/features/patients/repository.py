from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from app.features.patients.models import Patient, Document


class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, patient: Patient) -> Patient:
        self.db.add(patient)
        self.db.flush()
        return patient

    def get(self, patient_id: str) -> Patient | None:
        return self.db.get(Patient, patient_id)

    def search(self, query: str, page: int, page_size: int) -> tuple[list[Patient], int]:
        like = f"%{query}%"
        stmt = select(Patient).where(
            or_(Patient.first_name.ilike(like), Patient.last_name.ilike(like), Patient.phone.ilike(like))
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        items = self.db.scalars(
            stmt.order_by(Patient.last_name).offset((page - 1) * page_size).limit(page_size)
        ).all()
        return list(items), total

    def add_document(self, doc: Document) -> Document:
        self.db.add(doc)
        self.db.flush()
        return doc

    def list_documents(self, patient_id: str) -> list[Document]:
        return list(self.db.scalars(select(Document).where(Document.patient_id == patient_id)).all())

    def get_document(self, document_id: str) -> Document | None:
        return self.db.get(Document, document_id)
