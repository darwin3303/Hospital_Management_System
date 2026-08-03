import uuid

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), unique=True, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="UNPAID")
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    source_type = Column(String(20), nullable=False)  # CONSULTATION | LABORATORY | PHARMACY
    source_id = Column(UUID(as_uuid=True), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_payment_amount_positive"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(String(20), nullable=False)
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    paid_at = Column(DateTime(timezone=True), server_default=func.now())
