from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import UnauthorizedError, ForbiddenError
from app.core.roles import Role
from app.core.security import decode_access_token
from app.features.auth.models import User

# Using FastAPI's HTTPBearer (rather than a plain Header dependency) is what
# makes Swagger UI detect a security scheme and render the "Authorize" button.
bearer_scheme = HTTPBearer(auto_error=False)


def get_bearer_token(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Missing or malformed Authorization header.", code="MISSING_TOKEN")
    return credentials.credentials


def get_current_user(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise UnauthorizedError("Invalid or expired access token.", code="INVALID_TOKEN")

    user = db.get(User, payload["sub"])
    if user is None or not user.is_active:
        # Re-check DB state (not just the JWT claim) so a deactivated/role-changed
        # user is rejected even with an unexpired token.
        raise UnauthorizedError("Account is inactive or no longer exists.", code="ACCOUNT_INACTIVE")
    return user


def require_role(*allowed_roles: Role):
    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in {r.value for r in allowed_roles}:
            raise ForbiddenError(
                "You do not have permission to perform this action.",
                code="ROLE_NOT_PERMITTED",
                details={"required_roles": [r.value for r in allowed_roles]},
            )
        return current_user
    return _dependency