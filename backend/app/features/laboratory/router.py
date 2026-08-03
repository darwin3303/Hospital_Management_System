from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.roles import Role
from app.features.auth.models import User
from app.features.laboratory.schemas import LabRequestCreate, LabResultEntry, LabRequestOut
from app.features.laboratory.service import LaboratoryService

router = APIRouter(prefix="/lab-requests", tags=["laboratory"])


@router.post("", dependencies=[Depends(require_role(Role.DOCTOR))])
def create_lab_request(payload: LabRequestCreate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    req = LaboratoryService(db).create_request(payload, current_user)
    return {"success": True, "data": LabRequestOut.model_validate(req)}


@router.get("", dependencies=[Depends(require_role(Role.LAB_STAFF, Role.ADMIN, Role.DOCTOR))])
def lab_queue(status: str | None = "REQUESTED", db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = LaboratoryService(db).list_by_status(status)
    return {"success": True, "data": [LabRequestOut.model_validate(i) for i in items]}


@router.get("/medical-record/{medical_record_id}")
def list_for_record(medical_record_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = LaboratoryService(db).list_for_medical_record(medical_record_id)
    return {"success": True, "data": [LabRequestOut.model_validate(i) for i in items]}


@router.put("/{request_id}/collect-sample", dependencies=[Depends(require_role(Role.LAB_STAFF))])
def collect_sample(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = LaboratoryService(db).collect_sample(request_id, current_user)
    return {"success": True, "data": LabRequestOut.model_validate(req)}


@router.put("/{request_id}/enter-result", dependencies=[Depends(require_role(Role.LAB_STAFF))])
def enter_result(request_id: str, payload: LabResultEntry, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    req = LaboratoryService(db).enter_result(request_id, payload.result_data, current_user)
    return {"success": True, "data": LabRequestOut.model_validate(req)}


@router.put("/{request_id}/generate-report", dependencies=[Depends(require_role(Role.LAB_STAFF))])
def generate_report(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = LaboratoryService(db).generate_report(request_id, current_user)
    return {"success": True, "data": LabRequestOut.model_validate(req)}
