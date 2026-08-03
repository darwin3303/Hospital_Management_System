import uuid

from sqlalchemy import Column, String, Numeric, SmallInteger, Time, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), unique=True, nullable=False)
    specialty = Column(String(100), nullable=False)
    consultation_fee = Column(Numeric(10, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False, index=True)
    day_of_week = Column(SmallInteger, nullable=False)  # 0=Mon .. 6=Sun
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
