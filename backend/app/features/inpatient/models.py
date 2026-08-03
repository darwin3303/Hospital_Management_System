import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Admission(Base):
    __tablename__ = "admissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    admitted_at = Column(DateTime(timezone=True), server_default=func.now())
    discharge_medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=True)
    discharged_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    ward = Column(String(50), nullable=True)
    bed_number = Column(String(20), nullable=True)

    __table_args__ = (
        Index("idx_admission_one_active", "patient_id", unique=True,
              postgresql_where=(status == "ACTIVE")),
    )
