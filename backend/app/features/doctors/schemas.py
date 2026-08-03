from datetime import time
from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class AvailabilitySlot(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time


class DoctorCreate(BaseModel):
    employee_id: str
    specialty: str
    consultation_fee: float = 0
    availability: list[AvailabilitySlot] = []


class DoctorOut(ORMModel):
    id: str
    employee_id: str
    specialty: str
    consultation_fee: float


class AvailabilityOut(ORMModel):
    id: str
    day_of_week: int
    start_time: time
    end_time: time