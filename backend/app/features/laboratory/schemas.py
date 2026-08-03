from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class LabRequestCreate(BaseModel):
    medical_record_id: str
    test_name: str


class LabResultEntry(BaseModel):
    result_data: str


class LabRequestOut(ORMModel):
    id: str
    medical_record_id: str
    test_name: str
    status: str
    result_data: str | None