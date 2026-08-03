"""
One command to run before a demo. Checks, in order:
  1. Database connection reachable
  2. Alembic migrations are up to date (no pending revisions)
  3. At least one active Admin user exists
  4. The API server is reachable (if running)

Usage (from the backend/ folder, with venv active):
    python scripts/check_health.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CHECK = "  [OK] "
CROSS = "  [FAIL] "
WARN = "  [WARN] "


def check_database_connection() -> bool:
    from sqlalchemy import text
    from app.core.database import engine
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(CHECK + "Database connection reachable")
        return True
    except Exception as exc:
        print(CROSS + f"Database connection failed: {exc}")
        return False


def check_migrations_current() -> bool:
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    from alembic.runtime.migration import MigrationContext
    from app.core.database import engine

    try:
        cfg = Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
        script = ScriptDirectory.from_config(cfg)
        head_revision = script.get_current_head()

        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_revision = context.get_current_revision()

        if current_revision == head_revision:
            print(CHECK + f"Migrations up to date (revision {current_revision})")
            return True
        else:
            print(CROSS + f"Migrations out of date: DB at {current_revision}, "
                           f"latest is {head_revision}. Run 'alembic upgrade head'.")
            return False
    except Exception as exc:
        print(WARN + f"Could not verify migration state: {exc}")
        return False


def check_admin_exists() -> bool:
    from app.core.database import SessionLocal
    from app.features.auth.models import User

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == "ADMIN", User.is_active == True).first()  # noqa: E712
        if admin:
            print(CHECK + f"Active admin user exists ('{admin.username}')")
            return True
        else:
            print(CROSS + "No active admin user found. Run 'python scripts/seed_admin.py'.")
            return False
    except Exception as exc:
        print(CROSS + f"Could not check for admin user: {exc}")
        return False
    finally:
        db.close()


def check_api_reachable() -> bool:
    import urllib.request
    import urllib.error

    url = "http://localhost:8000/health"
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status == 200:
                print(CHECK + "API server is reachable at " + url)
                return True
            print(WARN + f"API server responded with status {response.status}")
            return False
    except urllib.error.URLError:
        print(WARN + "API server not reachable (is 'uvicorn app.main:app' running?)")
        return False


def main() -> None:
    print("Running pre-demo health check...\n")
    results = [
        check_database_connection(),
        check_migrations_current(),
        check_admin_exists(),
        check_api_reachable(),
    ]
    print()
    if all(results):
        print("All checks passed. Ready to demo.")
        sys.exit(0)
    else:
        print("One or more checks failed -- see above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
