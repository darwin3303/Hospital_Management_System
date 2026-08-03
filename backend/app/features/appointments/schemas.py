from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    scheduled_at: datetime
    duration_minutes: int = 30


class AppointmentRescheduleRequest(BaseModel):
    scheduled_at: datetime
    duration_minutes: int | None = None


class AppointmentOut(ORMModel):
    id: str
    patient_id: str
    doctor_id: str
    scheduled_at: datetime
    duration_minutes: int
    status: str