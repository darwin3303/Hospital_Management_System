from pydantic import BaseModel


class PatientReportRow(BaseModel):
    id: str
    first_name: str
    last_name: str
    phone: str


class AppointmentReportRow(BaseModel):
    id: str
    status: str
    scheduled_at: str


class RevenueReport(BaseModel):
    total_invoiced: float
    total_collected: float
    outstanding: float


class PharmacyReportRow(BaseModel):
    medicine_name: str
    quantity_in_stock: int


class LaboratoryReportRow(BaseModel):
    test_name: str
    status: str


class StaffReportRow(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    department_id: str
