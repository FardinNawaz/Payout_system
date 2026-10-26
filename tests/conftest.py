import os
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
import models

load_dotenv()
TEST_DATABASE_URL=os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL not found in .env")

test_engine=create_engine(TEST_DATABASE_URL)
TestingSessionLocal=sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)
def override_get_db():
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session",autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


