import uuid

from sqlalchemy import Column, String, Numeric, Integer, Date, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Medicine(Base):
    __tablename__ = "medicines"
    __table_args__ = (CheckConstraint("quantity_in_stock >= 0", name="ck_medicine_stock_nonneg"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    unit_price = Column(Numeric(10, 2), nullable=False, default=0)
    quantity_in_stock = Column(Integer, nullable=False, default=0)
    expiry_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PharmacyDispense(Base):
    __tablename__ = "pharmacy_dispenses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_item_id = Column(UUID(as_uuid=True), ForeignKey("prescription_items.id"), nullable=False, index=True)
    dispensed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    dispensed_at = Column(DateTime(timezone=True), server_default=func.now())
