from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.auth.models import User, RefreshToken


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def username_exists(self, username: str) -> bool:
        return self.db.scalar(select(User).where(User.username == username)) is not None

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def list_users(self, page: int, page_size: int) -> tuple[list[User], int]:
        from sqlalchemy import func
        items = self.db.scalars(
            select(User).order_by(User.username).offset((page - 1) * page_size).limit(page_size)
        ).all()
        total = self.db.scalar(select(func.count()).select_from(User))
        return list(items), total

    def create_refresh_token(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.flush()
        return token

    def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        return self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    def revoke_refresh_token(self, token: RefreshToken) -> None:
        from datetime import datetime, timezone
        token.revoked_at = datetime.now(timezone.utc)
        self.db.flush()
