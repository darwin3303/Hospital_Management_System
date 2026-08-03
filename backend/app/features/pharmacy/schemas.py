from datetime import date
from pydantic import BaseModel, ConfigDict
from app.core.schemas import ORMModel


class MedicineCreate(BaseModel):
    name: str
    unit_price: float
    quantity_in_stock: int
    expiry_date: date


class MedicineOut(ORMModel):
    id: str
    name: str
    unit_price: float
    quantity_in_stock: int
    expiry_date: date


class DispenseRequest(BaseModel):
    prescription_item_id: str
    quantity: int


class DispenseOut(ORMModel):
    id: str
    prescription_item_id: str
    quantity: int