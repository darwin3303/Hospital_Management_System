from datetime import date
from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    date_of_birth: date | None = None
    gender: str | None = None
    address: str | None = None


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None


class PatientOut(ORMModel):
    id: str
    first_name: str
    last_name: str
    phone: str
    date_of_birth: date | None
    gender: str | None
    address: str | None


class DocumentOut(ORMModel):
    id: str
    patient_id: str
    file_name: str
    file_path: str