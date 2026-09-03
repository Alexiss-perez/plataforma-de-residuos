from __future__ import annotations

import os
import sys
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_revinculo.db")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests-only")
os.environ.setdefault("AI_API_KEY", "")

from app.core.database import Base, get_db  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_engine) -> Generator[TestClient, None, None]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """Register a natural user and return auth headers."""
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "pass12345"},
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def collector_user_and_headers(client):
    """Register a collector user with profile."""
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Collector User",
            "email": "collector@example.com",
            "password": "pass12345",
            "role": "COLLECTOR",
            "can_collect": True,
            "commune": "Santiago",
            "latitude": -33.45,
            "longitude": -70.65,
        },
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = resp.json()["user"]["id"]
    resp2 = client.post(
        "/api/v1/collectors/profile",
        json={
            "vehicle_type": "Camioneta",
            "max_weight_kg": 500,
            "radius_km": 30,
            "available": True,
            "materials_accepted": ["WOOD", "METAL", "FURNITURE"],
            "description": "Recolector con camioneta",
        },
        headers=headers,
    )
    assert resp2.status_code == 201, resp2.text
    return user_id, headers


@pytest.fixture
def org_user_and_headers(client):
    """Register an organization user with org and return headers + org_id."""
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Org User",
            "email": "org@example.com",
            "password": "pass12345",
            "role": "ORGANIZATION",
            "commune": "Providencia",
            "latitude": -33.45,
            "longitude": -70.66,
        },
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp2 = client.post(
        "/api/v1/organizations",
        json={"name": "Fundación Test", "type": "FOUNDATION", "description": "Test org", "commune": "Providencia", "latitude": -33.45, "longitude": -70.66},
        headers=headers,
    )
    assert resp2.status_code == 201, resp2.text
    org_id = resp2.json()["id"]
    return org_id, headers
