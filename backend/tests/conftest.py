import os
from pathlib import Path

os.environ['DATABASE_URL'] = f"sqlite:///{(Path(__file__).parent / 'test_auth.db').as_posix()}"
os.environ['JWT_SECRET_KEY'] = 'test-secret'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['JWT_EXPIRE_MINUTES'] = '120'

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app


@pytest.fixture(autouse=True)
def prepare_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
