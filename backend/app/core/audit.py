import uuid

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), nullable=True)
    actor_user_id = Column(UUID(as_uuid=True), nullable=True)
    actor_role = Column(String(20), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def write_audit_log(
    db: Session,
    *,
    actor_user_id: str | None,
    actor_role: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None,
    request_id: str | None = None,
) -> None:
    """Called from within a service method's transaction, never on its own,
    so an audit row can never exist without its action having committed."""
    db.add(AuditLog(
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        request_id=request_id,
    ))
