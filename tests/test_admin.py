import sys
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure backend directory is in sys.path
backend_path = str(Path(__file__).resolve().parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.agent import Agent
from app.models.team import Team


@pytest_asyncio.fixture
async def async_test_client():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSession() as seed_session:
        team = Team(name="Technical Support")
        seed_session.add(team)
        await seed_session.commit()

        ag = Agent(name="Agent 1", email="ag1@example.com", team_id=team.id, skills="Technical", current_workload=0, availability="Available")
        seed_session.add(ag)
        await seed_session.commit()

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


async def get_token(client: AsyncClient, email: str, role: str = "user"):
    payload = {"name": "Test User", "email": email, "password": "Password123!", "role": role}
    res = await client.post("/api/v1/auth/register", json=payload)
    return res.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_admin_access_control(async_test_client):
    user_token = await get_token(async_test_client, "regular_user@example.com", role="user")
    admin_token = await get_token(async_test_client, "admin_user@example.com", role="admin")

    h_user = {"Authorization": f"Bearer {user_token}"}
    h_admin = {"Authorization": f"Bearer {admin_token}"}

    # Regular user receives 403 Forbidden
    res_user = await async_test_client.get("/api/v1/admin/analytics", headers=h_user)
    assert res_user.status_code == 403

    # Admin receives 200 OK
    res_admin = await async_test_client.get("/api/v1/admin/analytics", headers=h_admin)
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert "total_complaints" in data
    assert "total_tickets" in data


@pytest.mark.asyncio
async def test_admin_agent_list_and_user_list(async_test_client):
    admin_token = await get_token(async_test_client, "admin_user2@example.com", role="admin")
    h_admin = {"Authorization": f"Bearer {admin_token}"}

    # User list
    users_res = await async_test_client.get("/api/v1/admin/users", headers=h_admin)
    assert users_res.status_code == 200
    assert users_res.json()["total"] >= 1

    # Agents list
    agents_res = await async_test_client.get("/api/v1/admin/agents", headers=h_admin)
    assert agents_res.status_code == 200
    agents_data = agents_res.json()
    assert len(agents_data) >= 1
    assert agents_data[0]["name"] == "Agent 1"


@pytest.mark.asyncio
async def test_admin_manual_assignment(async_test_client):
    admin_token = await get_token(async_test_client, "admin_user3@example.com", role="admin")
    h_admin = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create complaint and ticket
    cmp_res = await async_test_client.post("/api/v1/complaints", json={"text": "Technical glitch on login"}, headers=h_admin)
    ticket_id = cmp_res.json()["ticket_id"]

    # 2. Get Agent ID
    agents_res = await async_test_client.get("/api/v1/admin/agents", headers=h_admin)
    agent_id = agents_res.json()[0]["id"]

    # 3. Assign ticket to Agent
    assign_res = await async_test_client.put(
        f"/api/v1/admin/tickets/{ticket_id}/assign",
        json={"agent_id": agent_id},
        headers=h_admin,
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_agent_id"] == agent_id
