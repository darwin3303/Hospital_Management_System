import uuid

from sqlalchemy.orm import Session

from app.core.audit import write_audit_log
from app.core.errors import UnauthorizedError, ConflictError, ForbiddenError, NotFoundError
from app.core.security import (
    hash_password, verify_password, create_access_token,
    generate_refresh_token_raw, hash_refresh_token, refresh_token_expiry,
)
from app.features.auth import domain
from app.features.auth.models import User, RefreshToken
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import CreateUserRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuthRepository(db)

    # ---- Login / logout / refresh -------------------------------------

    def login(self, username: str, password: str, request_id: str | None = None) -> tuple[str, str, User]:
        user = self.repo.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid username or password.", code="INVALID_CREDENTIALS")

        if not domain.is_login_allowed(user.is_active):
            raise UnauthorizedError("This account has been deactivated.", code="ACCOUNT_INACTIVE")

        access_token = create_access_token(str(user.id), user.role)
        raw_refresh = generate_refresh_token_raw()

        self.repo.create_refresh_token(RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh),
            expires_at=refresh_token_expiry(),
        ))
        write_audit_log(self.db, actor_user_id=str(user.id), actor_role=user.role,
                         action="LOGIN", entity_type="User", entity_id=str(user.id), request_id=request_id)
        self.db.commit()
        return access_token, raw_refresh, user

    def refresh(self, raw_refresh_token: str, request_id: str | None = None) -> tuple[str, str]:
        token_hash = hash_refresh_token(raw_refresh_token)
        token = self.repo.get_refresh_token_by_hash(token_hash)
        if token is None or not domain.is_refresh_token_valid(token.revoked_at, token.expires_at):
            raise UnauthorizedError("Refresh token is invalid, expired, or revoked.", code="INVALID_REFRESH_TOKEN")

        user = self.repo.get_by_id(str(token.user_id))
        if user is None or not user.is_active:
            raise UnauthorizedError("Account is inactive.", code="ACCOUNT_INACTIVE")

        # Rotate: revoke old, issue new — limits the window a stolen token is usable.
        self.repo.revoke_refresh_token(token)
        new_raw = generate_refresh_token_raw()
        self.repo.create_refresh_token(RefreshToken(
            user_id=user.id, token_hash=hash_refresh_token(new_raw), expires_at=refresh_token_expiry(),
        ))
        access_token = create_access_token(str(user.id), user.role)
        self.db.commit()
        return access_token, new_raw

    def logout(self, raw_refresh_token: str, actor: User, request_id: str | None = None) -> None:
        token_hash = hash_refresh_token(raw_refresh_token)
        token = self.repo.get_refresh_token_by_hash(token_hash)
        if token is not None:
            self.repo.revoke_refresh_token(token)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="LOGOUT", entity_type="User", entity_id=str(actor.id), request_id=request_id)
        self.db.commit()

    # ---- User administration -------------------------------------------

    def create_user(self, payload: CreateUserRequest, actor: User, request_id: str | None = None) -> User:
        if self.repo.username_exists(payload.username):
            raise ConflictError("Username already exists.", code="USERNAME_TAKEN")

        user = User(
            id=uuid.uuid4(),
            username=payload.username,
            password_hash=hash_password(payload.password),
            role=payload.role,
            is_active=True,
        )
        self.repo.create_user(user)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CREATE_USER", entity_type="User", entity_id=str(user.id), request_id=request_id)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, page: int, page_size: int) -> tuple[list[User], int]:
        return self.repo.list_users(page, page_size)

    def set_user_status(self, target_user_id: str, is_active: bool, actor: User,
                         request_id: str | None = None) -> User:
        target = self.repo.get_by_id(target_user_id)
        if target is None:
            raise NotFoundError("User not found.", code="USER_NOT_FOUND")

        if not is_active and not domain.can_deactivate(str(target.id), str(actor.id)):
            raise ForbiddenError("You cannot deactivate your own account.", code="SELF_DEACTIVATION_BLOCKED")

        target.is_active = is_active
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="SET_USER_STATUS", entity_type="User", entity_id=str(target.id),
                         request_id=request_id)
        self.db.commit()
        self.db.refresh(target)
        return target

    def change_password(self, actor: User, old_password: str, new_password: str,
                         request_id: str | None = None) -> None:
        if not verify_password(old_password, actor.password_hash):
            raise UnauthorizedError("Current password is incorrect.", code="INVALID_CREDENTIALS")
        actor.password_hash = hash_password(new_password)
        write_audit_log(self.db, actor_user_id=str(actor.id), actor_role=actor.role,
                         action="CHANGE_PASSWORD", entity_type="User", entity_id=str(actor.id),
                         request_id=request_id)
        self.db.commit()
