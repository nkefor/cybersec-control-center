"""Tests for identity endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

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
async def test_list_users_empty(client):
    response = await client.get("/api/identity/users")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_mfa_summary_empty(client):
    response = await client.get("/api/identity/mfa-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 0
    assert data["mfa_enabled"] == 0
    assert data["coverage_percentage"] == 0.0


@pytest.mark.asyncio
async def test_inactive_users_empty(client):
    response = await client.get("/api/identity/inactive-users")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_user_list_pagination(client):
    response = await client.get("/api/identity/users?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "page_size" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
