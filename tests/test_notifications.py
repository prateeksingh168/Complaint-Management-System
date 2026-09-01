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


@pytest_asyncio.fixture
async def async_test_client():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSession() as seed_session:
        cats = [Category(name="Other", is_active=True), Category(name="Billing", is_active=True)]
        seed_session.add_all(cats)
        await seed_session.commit()

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


async def get_auth_token(client: AsyncClient, email: str, role: str = "user"):
    payload = {"name": "Test User", "email": email, "password": "Password123!", "role": role}
    res = await client.post("/api/v1/auth/register", json=payload)
    return res.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_notification_flow_on_ticket_status_change(async_test_client):
    user_token = await get_auth_token(async_test_client, "notif_user@example.com", role="user")
    agent_token = await get_auth_token(async_test_client, "notif_agent@example.com", role="agent")

    user_h = {"Authorization": f"Bearer {user_token}"}
    agent_h = {"Authorization": f"Bearer {agent_token}"}

    # 1. User creates complaint
    cmp_res = await async_test_client.post(
        "/api/v1/complaints",
        json={"text": "Incorrect charge on my billing invoice statement"},
        headers=user_h,
    )
    ticket_id = cmp_res.json()["ticket_id"]

    # 2. Agent updates ticket status to 'In Progress'
    await async_test_client.put(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "In Progress", "note": "Agent investigating"},
        headers=agent_h,
    )

    # 3. User checks notifications
    notif_res = await async_test_client.get("/api/v1/notifications", headers=user_h)
    assert notif_res.status_code == 200
    data = notif_res.json()
    assert data["total"] >= 1
    
    first_notif = data["items"][0]
    assert "In Progress" in first_notif["message"]
    assert first_notif["is_read"] is False

    # 4. Mark notification as read
    read_res = await async_test_client.put(f"/api/v1/notifications/{first_notif['id']}/read", headers=user_h)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True
