from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.roles import Role
from app.features.auth.models import User
from app.features.inpatient.schemas import AdmissionCreate, DischargeRequest, AdmissionOut
from app.features.inpatient.service import InpatientService

router = APIRouter(prefix="/admissions", tags=["inpatient"])


@router.post("", dependencies=[Depends(require_role(Role.ADMIN, Role.DOCTOR, Role.RECEPTIONIST))])
def admit_patient(payload: AdmissionCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    admission = InpatientService(db).admit(payload, current_user)
    return {"success": True, "data": AdmissionOut.model_validate(admission)}


@router.get("/{admission_id}")
def get_admission(admission_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    admission = InpatientService(db).get(admission_id)
    return {"success": True, "data": AdmissionOut.model_validate(admission)}


@router.put("/{admission_id}/discharge", dependencies=[Depends(require_role(Role.DOCTOR, Role.ADMIN))])
def discharge_patient(admission_id: str, payload: DischargeRequest, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    admission = InpatientService(db).discharge(admission_id, payload.discharge_medical_record_id, current_user)
    return {"success": True, "data": AdmissionOut.model_validate(admission)}
