from app.core.database import SessionLocal
from app.core.security import hash_password
from app.features.auth.models import User
import uuid

db = SessionLocal()
db.add(User(
    id=uuid.uuid4(),
    username="admin",
    password_hash=hash_password("Admin@1234"),
    role="ADMIN",
    is_active=True,
))
db.commit()
print("Admin created: username=admin password=Admin@1234")