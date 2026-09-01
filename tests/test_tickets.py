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
from app.models.category import Category
from app.models.team import Team


@pytest_asyncio.fixture
async def async_test_client():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    # Seed categories and teams
    async with TestSession() as seed_session:
        cats = [
            Category(name="Other", is_active=True),
            Category(name="Billing", is_active=True),
            Category(name="Technical", is_active=True),
        ]
        teams = [
            Team(name="General Support", is_active=True),
            Team(name="Technical Support", is_active=True),
        ]
        seed_session.add_all(cats + teams)
        await seed_session.commit()

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


async def get_auth_header(client: AsyncClient, email: str, role: str = "user"):
    payload = {"name": "Test User", "email": email, "password": "Password123!", "role": role}
    res = await client.post("/api/v1/auth/register", json=payload)
    token = res.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ticket_status_state_machine_and_history(async_test_client):
    user_header = await get_auth_header(async_test_client, "user_ticket@example.com")
    agent_header = await get_auth_header(async_test_client, "agent_ticket@example.com", role="agent")

    # 1. Create Complaint (which spawns Ticket)
    cmp_res = await async_test_client.post(
        "/api/v1/complaints",
        json={"text": "System crash error when opening billing page"},
        headers=user_header,
    )
    cmp_data = cmp_res.json()
    ticket_id = cmp_data["ticket_id"]

    # Verify initial status is 'Registered'
    t1_res = await async_test_client.get(f"/api/v1/tickets/{ticket_id}", headers=agent_header)
    assert t1_res.status_code == 200
    assert t1_res.json()["status"] == "Registered"

    # 2. Transition Registered -> In Progress (Valid)
    status_payload_1 = {"status": "In Progress", "note": "Assigned to agent John"}
    t2_res = await async_test_client.put(
        f"/api/v1/tickets/{ticket_id}/status",
        json=status_payload_1,
        headers=agent_header,
    )
    assert t2_res.status_code == 200
    assert t2_res.json()["status"] == "In Progress"

    # 3. Transition In Progress -> Resolved (Valid)
    status_payload_2 = {"status": "Resolved", "note": "Issue resolved by clearing cache"}
    t3_res = await async_test_client.put(
        f"/api/v1/tickets/{ticket_id}/status",
        json=status_payload_2,
        headers=agent_header,
    )
    assert t3_res.status_code == 200
    t3_data = t3_res.json()
    assert t3_data["status"] == "Resolved"
    assert t3_data["resolved_at"] is not None

    # Check history rows recorded
    history = t3_data["history"]
    assert len(history) == 2
    assert history[0]["new_status"] == "Resolved"
    assert history[1]["new_status"] == "In Progress"

    # 4. Attempt invalid transition Resolved -> Registered (Invalid jump, should return 400)
    invalid_res = await async_test_client.put(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "Registered", "note": "Reopening"},
        headers=agent_header,
    )
    assert invalid_res.status_code == 400
    res_data = invalid_res.json()
    error_msg = res_data.get("error", {}).get("message") or res_data.get("detail", "")
    assert "Invalid status transition" in error_msg


@pytest.mark.asyncio
async def test_list_tickets_filtering(async_test_client):
    admin_header = await get_auth_header(async_test_client, "admin_tickets@example.com", role="admin")

    # Create complaints
    await async_test_client.post(
        "/api/v1/complaints",
        json={"text": "Delivery delay issue"},
        headers=admin_header,
    )

    list_res = await async_test_client.get("/api/v1/tickets?status=Registered", headers=admin_header)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1
