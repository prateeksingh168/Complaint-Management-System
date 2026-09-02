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
from app.models.team import Team


@pytest_asyncio.fixture
async def async_test_client():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSession() as seed_session:
        teams = [
            Team(name="General Support"),
            Team(name="Billing Support"),
            Team(name="Technical Support"),
        ]
        seed_session.add_all(teams)
        await seed_session.commit()

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


async def get_user_auth_headers(client: AsyncClient):
    payload = {
        "name": "Complaint User",
        "email": "complaint.user@example.com",
        "password": "Password123!",
        "role": "user"
    }
    res = await client.post("/api/v1/auth/register", json=payload)
    token = res.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_complaint_and_linked_ticket(async_test_client):
    headers = await get_user_auth_headers(async_test_client)
    
    complaint_payload = {
        "text": "Money was deducted from my account but the transaction failed.",
        "category": "Billing",
        "priority": "High"
    }

    response = await async_test_client.post("/api/v1/complaints", json=complaint_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["complaint_id"].startswith("CMP-")
    assert data["category"] == "Billing"
    assert data["priority"] == "High"
    assert data["ticket_id"] is not None


@pytest.mark.asyncio
async def test_list_complaints_pagination(async_test_client):
    headers = await get_user_auth_headers(async_test_client)

    for i in range(3):
        await async_test_client.post(
            "/api/v1/complaints",
            json={"text": f"Technical issue number {i} with service"},
            headers=headers
        )

    response = await async_test_client.get("/api/v1/complaints?page=1&page_size=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) == 2
