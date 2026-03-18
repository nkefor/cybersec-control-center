"""Tests for task CRUD endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.seed import seed_demo_data

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
async def test_list_tasks_empty(client):
    response = await client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_task(client):
    payload = {
        "title": "Test task",
        "description": "A test task description",
        "priority": "high",
    }
    response = await client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert "id" in data


@pytest.mark.asyncio
async def test_update_task_status(client):
    # Create a task first
    create_resp = await client.post("/api/tasks", json={"title": "Update me", "priority": "medium"})
    task_id = create_resp.json()["id"]

    # Update it
    update_resp = await client.patch(f"/api/tasks/{task_id}", json={"status": "in_progress"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_task(client):
    create_resp = await client.post("/api/tasks", json={"title": "Delete me", "priority": "low"})
    task_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/tasks/{task_id}")
    assert delete_resp.status_code == 204

    # Verify deleted
    list_resp = await client.get("/api/tasks")
    ids = [t["id"] for t in list_resp.json()["items"]]
    assert task_id not in ids
