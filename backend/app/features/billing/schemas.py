from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class InvoiceGenerateRequest(BaseModel):
    appointment_id: str


class LineItemOut(ORMModel):
    id: str
    source_type: str
    source_id: str
    description: str
    amount: float


class InvoiceOut(ORMModel):
    id: str
    appointment_id: str
    total_amount: float
    status: str
    line_items: list[LineItemOut] = []


class PaymentRequest(BaseModel):
    amount: float
    method: str


class PaymentOut(ORMModel):
    id: str
    invoice_id: str
    amount: float
    method: str