import uuid

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), unique=True, nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    diagnosis = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MedicalRecordAmendment(Base):
    __tablename__ = "medical_record_amendments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False, index=True)
    amended_text = Column(Text, nullable=False)
    amended_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amended_at = Column(DateTime(timezone=True), server_default=func.now())


class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False, index=True)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    dosage_instructions = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="PENDING", index=True)
