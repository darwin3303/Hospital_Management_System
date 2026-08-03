import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class LabRequest(Base):
    __tablename__ = "lab_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False, index=True)
    test_name = Column(String(200), nullable=False)
    status = Column(String(30), nullable=False, default="REQUESTED", index=True)
    result_data = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
