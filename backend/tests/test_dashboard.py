"""Tests for the dashboard summary endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_dashboard_summary_empty_db(client):
    """Dashboard should return zeroed metrics when DB has no data."""
    response = await client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "security_score" in data
    assert "mfa_coverage" in data
    assert "devices" in data
    assert "backups" in data
    assert data["mfa_coverage"]["total"] == 0
    assert data["devices"]["total"] == 0


@pytest.mark.asyncio
async def test_dashboard_returns_all_fields(client):
    """All expected fields should be present in the response."""
    response = await client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()

    required_fields = [
        "security_score", "score_change_7d", "mfa_coverage",
        "risky_logins_24h", "devices", "backups",
        "open_tasks", "critical_incidents", "tenant_name",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
