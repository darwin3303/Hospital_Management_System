import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.pagination import page_params, paginate_meta, PageParams
from app.core.roles import Role
from app.features.auth.models import User
from app.features.patients.schemas import PatientCreate, PatientUpdate, PatientOut, DocumentOut
from app.features.patients.service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def register_patient(payload: PatientCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    patient = PatientService(db).register(payload, current_user)
    return {"success": True, "data": PatientOut.model_validate(patient)}


@router.get("/search")
def search_patients(query: str, db: Session = Depends(get_db), pagination: PageParams = Depends(page_params),
                     _=Depends(get_current_user)):
    items, total = PatientService(db).search(query, pagination.page, pagination.page_size)
    return {"success": True, "data": [PatientOut.model_validate(p) for p in items],
            "meta": paginate_meta(pagination.page, pagination.page_size, total)}


@router.get("/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    patient = PatientService(db).get(patient_id)
    return {"success": True, "data": PatientOut.model_validate(patient)}


@router.put("/{patient_id}", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def update_patient(patient_id: str, payload: PatientUpdate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    patient = PatientService(db).update(patient_id, payload, current_user)
    return {"success": True, "data": PatientOut.model_validate(patient)}


@router.post("/{patient_id}/documents", dependencies=[Depends(require_role(Role.ADMIN, Role.RECEPTIONIST))])
def upload_document(patient_id: str, file: UploadFile = File(...), db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    stored_name = f"{uuid.uuid4()}_{file.filename}"
    dest_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(dest_path, "wb") as f:
        f.write(file.file.read())
    doc = PatientService(db).upload_document(patient_id, file.filename, dest_path, current_user)
    return {"success": True, "data": DocumentOut.model_validate(doc)}


@router.get("/{patient_id}/documents")
def list_documents(patient_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    docs = PatientService(db).list_documents(patient_id)
    return {"success": True, "data": [DocumentOut.model_validate(d) for d in docs]}


@router.get("/documents/{document_id}/download")
def download_document(document_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    doc = PatientService(db).get_document(document_id)
    return FileResponse(doc.file_path, filename=doc.file_name)
