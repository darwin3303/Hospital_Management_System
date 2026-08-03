"""
Drops and recreates every table via SQLAlchemy metadata. For local
development resets only -- never point this at anything you care about.

Usage (from the backend/ folder, with venv active):
    python scripts/reset_db.py
    python scripts/reset_db.py --yes    (skip the confirmation prompt)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, engine
from app.shared import models_registry  # noqa: F401 -- populates Base.metadata


def reset_db(skip_confirm: bool = False) -> None:
    if not skip_confirm:
        answer = input(
            f"This will DROP ALL TABLES on {engine.url.database}. Type 'yes' to continue: "
        )
        if answer.strip().lower() != "yes":
            print("Aborted.")
            return

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print(f"Database '{engine.url.database}' reset: all tables dropped and recreated.")
    print("Note: this bypasses Alembic. Run 'alembic stamp head' afterward if you want "
          "migration history to reflect the current schema state.")


if __name__ == "__main__":
    reset_db(skip_confirm="--yes" in sys.argv)
