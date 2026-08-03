from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.roles import Role
from app.features.auth.models import User
from app.features.emr.schemas import PrescriptionItemOut
from app.features.pharmacy.schemas import MedicineCreate, MedicineOut, DispenseRequest, DispenseOut
from app.features.pharmacy.service import PharmacyService

router = APIRouter(prefix="/pharmacy", tags=["pharmacy"])


@router.post("/medicines", dependencies=[Depends(require_role(Role.PHARMACIST, Role.ADMIN))])
def add_medicine(payload: MedicineCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    medicine = PharmacyService(db).add_medicine(payload, current_user)
    return {"success": True, "data": MedicineOut.model_validate(medicine)}


@router.get("/medicines")
def list_medicines(db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = PharmacyService(db).list_medicines()
    return {"success": True, "data": [MedicineOut.model_validate(m) for m in items]}


@router.get("/prescriptions/pending", dependencies=[Depends(require_role(Role.PHARMACIST, Role.ADMIN))])
def pending_prescriptions(db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = PharmacyService(db).list_pending_prescriptions()
    return {"success": True, "data": [PrescriptionItemOut.model_validate(i) for i in items]}


@router.post("/dispense", dependencies=[Depends(require_role(Role.PHARMACIST))])
def dispense(payload: DispenseRequest, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    result = PharmacyService(db).dispense(payload, current_user)
    return {"success": True, "data": DispenseOut.model_validate(result)}
