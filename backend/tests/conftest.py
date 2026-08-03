import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/hms_test_db")
os.environ.setdefault("JWT_SECRET", "test_jwt_secret")
os.environ.setdefault("REFRESH_SECRET", "test_refresh_secret")
os.environ.setdefault("CLIENT_ORIGIN", "http://localhost:5173")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.shared import models_registry  # noqa: F401 -- populates Base.metadata
from app.main import app


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture()
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    from fastapi.testclient import TestClient

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
