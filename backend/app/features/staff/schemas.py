from datetime import date
from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class DepartmentCreate(BaseModel):
    name: str


class DepartmentOut(ORMModel):
    id: str
    name: str


class EmployeeCreate(BaseModel):
    user_id: str | None = None
    department_id: str
    first_name: str
    last_name: str
    phone: str | None = None
    hired_at: date | None = None


class EmployeeOut(ORMModel):
    id: str
    user_id: str | None
    department_id: str
    first_name: str
    last_name: str
    phone: str | None
    hired_at: date


class AttendanceMarkRequest(BaseModel):
    employee_id: str
    status: str = "PRESENT"


class AttendanceOut(ORMModel):
    id: str
    employee_id: str
    date: date
    status: str


class LeaveRequestCreate(BaseModel):
    employee_id: str
    start_date: date
    end_date: date
    reason: str | None = None


class LeaveDecisionRequest(BaseModel):
    approve: bool


class LeaveRequestOut(ORMModel):
    id: str
    employee_id: str
    start_date: date
    end_date: date
    status: str