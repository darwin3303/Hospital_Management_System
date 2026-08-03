from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class AdmissionCreate(BaseModel):
    patient_id: str
    appointment_id: str | None = None
    ward: str | None = None
    bed_number: str | None = None


class DischargeRequest(BaseModel):
    discharge_medical_record_id: str


class AdmissionOut(ORMModel):
    id: str
    patient_id: str
    status: str
    ward: str | None
    bed_number: str | None