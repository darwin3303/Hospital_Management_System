import uuid

from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import NotFoundError
from app.features.auth.models import User
from app.features.patients.models import Patient, Document
from app.features.patients.repository import PatientRepository
from app.features.patients.schemas import PatientCreate, PatientUpdate


class PatientService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PatientRepository(db)

    def register(self, payload: PatientCreate, actor: User) -> Patient:
        patient = Patient(id=uuid.uuid4(), **payload.model_dump())
        self.repo.create(patient)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="REGISTER_PATIENT", entity_type="Patient", entity_id=str(patient.id))
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get(self, patient_id: str) -> Patient:
        patient = self.repo.get(patient_id)
        if patient is None:
            raise NotFoundError("Patient not found.", code="PATIENT_NOT_FOUND")
        return patient

    def update(self, patient_id: str, payload: PatientUpdate, actor: User) -> Patient:
        patient = self.get(patient_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(patient, field, value)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="UPDATE_PATIENT", entity_type="Patient", entity_id=str(patient.id))
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def search(self, query: str, page: int, page_size: int) -> tuple[list[Patient], int]:
        return self.repo.search(query, page, page_size)

    def upload_document(self, patient_id: str, file_name: str, file_path: str, actor: User) -> Document:
        if self.repo.get(patient_id) is None:
            raise NotFoundError("Patient not found.", code="PATIENT_NOT_FOUND")
        doc = Document(id=uuid.uuid4(), patient_id=patient_id, file_name=file_name,
                        file_path=file_path, uploaded_by=actor.id)
        self.repo.add_document(doc)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="UPLOAD_DOCUMENT", entity_type="Document", entity_id=str(doc.id))
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def list_documents(self, patient_id: str) -> list[Document]:
        return self.repo.list_documents(patient_id)

    def get_document(self, document_id: str) -> Document:
        doc = self.repo.get_document(document_id)
        if doc is None:
            raise NotFoundError("Document not found.", code="DOCUMENT_NOT_FOUND")
        return doc
