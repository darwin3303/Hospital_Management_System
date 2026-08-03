"""Pure business rules for auth. No SQLAlchemy, no FastAPI imports here."""
from datetime import datetime, timezone


def is_login_allowed(is_active: bool) -> bool:
    return is_active


def is_refresh_token_valid(revoked_at, expires_at) -> bool:
    if revoked_at is not None:
        return False
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at > datetime.now(timezone.utc)


def can_deactivate(target_user_id: str, acting_user_id: str) -> bool:
    """R21: Admin cannot deactivate their own account."""
    return target_user_id != acting_user_id
