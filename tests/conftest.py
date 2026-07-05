import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base

from unittest.mock import MagicMock

from app.models.monitor import Monitor
from app.models.monitor_check import MonitorCheck

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db

TEST_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost:5432/api_monitor_test"
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture(scope="session", autouse=True)
def create_test_database():

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_database():

    connection = TestingSessionLocal()

    try:
        yield
    finally:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        connection.close()

@pytest.fixture
def db():

    connection = TestingSessionLocal()

    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()

def override_get_db():
    connection = TestingSessionLocal()

    try:
        yield connection
    finally:
        connection.close()


app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def sample_monitor():
    return Monitor(
        id=1,
        name="Google",
        url="https://google.com"
    )


@pytest.fixture
def sample_monitor_up():
    return MonitorCheck(
        monitor_id=1,
        status_code=200,
        response_time_ms=250,
        is_up=True
    )


@pytest.fixture
def sample_monitor_down():
    return MonitorCheck(
        monitor_id=1,
        status_code=500,
        response_time_ms=5000,
        is_up=False
    )

@pytest.fixture
def sample_monitor_payload():
    return {
        "name": "Google",
        "url": "https://google.com",
        "interval_minutes": 5
    }

@pytest.fixture
def sample_monitor_check():

    return MonitorCheck(
        status_code=200,
        response_time_ms=300,
        is_up=True
    )