"""
Creates the first Admin user, needed to bootstrap the system since every
other user-creation endpoint requires an existing Admin token.

Usage (from the backend/ folder, with venv active):
    python scripts/seed_admin.py
"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.features.auth.models import User

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "Admin@1234"


def seed_admin(username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"Admin user '{username}' already exists (id={existing.id}). Nothing to do.")
            return

        db.add(User(
            id=uuid.uuid4(),
            username=username,
            password_hash=hash_password(password),
            role="ADMIN",
            is_active=True,
        ))
        db.commit()
        print(f"Admin created: username={username} password={password}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
