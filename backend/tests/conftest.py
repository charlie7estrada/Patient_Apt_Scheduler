import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import User, UserRole
from app.services.auth import hash_password
from app.services.seed import DEMO_PROVIDER_EMAIL


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def provider(db_session):
    provider = User(
        email=DEMO_PROVIDER_EMAIL,
        hashed_password=hash_password("not-used-for-login"),
        full_name="Dr. Demo",
        role=UserRole.provider,
    )
    db_session.add(provider)
    db_session.commit()
    db_session.refresh(provider)
    return provider


@pytest.fixture()
def patient(db_session):
    patient = User(
        email="patient@example.com",
        hashed_password=hash_password("securepassword123"),
        full_name="Test Patient",
        role=UserRole.patient,
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient