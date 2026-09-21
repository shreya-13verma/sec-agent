import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.insert(0, "/home/shreya/compliance-agent")

from backend.app.config import settings
from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.utils.seed_data import seed_database
from backend.app.utils.security import create_access_token

# Use in-memory SQLite for test isolation
TEST_DATABASE_URL = "sqlite:///:memory:"
engine_test = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)

@pytest.fixture(scope="function")
def db_session():
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_headers():
    token = create_access_token({"sub": "admin", "role": "Admin", "id": 1})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sec_officer_headers():
    token = create_access_token({"sub": "sec_officer", "role": "Security_Officer", "id": 2})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def operator_headers():
    token = create_access_token({"sub": "operator", "role": "Operator", "id": 3})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auditor_headers():
    token = create_access_token({"sub": "auditor", "role": "Auditor", "id": 4})
    return {"Authorization": f"Bearer {token}"}
