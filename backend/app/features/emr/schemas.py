from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class MedicalRecordCreate(BaseModel):
    appointment_id: str
    diagnosis: str
    notes: str | None = None


class MedicalRecordOut(ORMModel):
    id: str
    appointment_id: str
    doctor_id: str
    patient_id: str
    diagnosis: str
    notes: str | None


class AmendmentCreate(BaseModel):
    amended_text: str


class AmendmentOut(ORMModel):
    id: str
    medical_record_id: str
    amended_text: str


class PrescriptionItemCreate(BaseModel):
    medicine_id: str
    quantity: int
    dosage_instructions: str | None = None


class PrescriptionCreate(BaseModel):
    items: list[PrescriptionItemCreate]


class PrescriptionItemOut(ORMModel):
    id: str
    medicine_id: str
    quantity: int
    status: str


class PrescriptionOut(ORMModel):
    id: str
    medical_record_id: str
    items: list[PrescriptionItemOut] = []