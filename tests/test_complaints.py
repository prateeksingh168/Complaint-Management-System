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

    # Seed categories table
    async with TestSession() as seed_session:
        cats = [
            Category(name="Other", is_active=True),
            Category(name="Billing", is_active=True),
            Category(name="Technical", is_active=True),
            Category(name="Delivery", is_active=True),
            Category(name="Service", is_active=True),
            Category(name="Account", is_active=True),
        ]
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


async def register_and_get_token(client: AsyncClient, email: str, name: str = "Test User", role: str = "user"):
    payload = {"name": name, "email": email, "password": "Password123!", "role": role}
    res = await client.post("/api/v1/auth/register", json=payload)
    return res.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_create_complaint_with_fallback_classification(async_test_client):
    token = await register_and_get_token(async_test_client, "user1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"text": "I was double charged on my invoice and need a refund for my billing statement."}
    response = await async_test_client.post("/api/v1/complaints", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["complaint_id"].startswith("CMP-")
    assert data["priority"] in ["High", "Medium", "Urgent"]
    assert data["category"]["name"] == "Billing"
    assert data["ticket_id"] is not None


@pytest.mark.asyncio
async def test_list_complaints_pagination_and_ownership(async_test_client):
    user1_token = await register_and_get_token(async_test_client, "user2@example.com")
    user2_token = await register_and_get_token(async_test_client, "user3@example.com")
    admin_token = await register_and_get_token(async_test_client, "admin1@example.com", role="admin")

    h1 = {"Authorization": f"Bearer {user1_token}"}
    h2 = {"Authorization": f"Bearer {user2_token}"}
    h_admin = {"Authorization": f"Bearer {admin_token}"}

    # User 1 creates 2 complaints
    await async_test_client.post("/api/v1/complaints", json={"text": "Technical crash on mobile app"}, headers=h1)
    await async_test_client.post("/api/v1/complaints", json={"text": "Delivery delay of my package"}, headers=h1)

    # User 2 creates 1 complaint
    await async_test_client.post("/api/v1/complaints", json={"text": "Password reset login issue"}, headers=h2)

    # User 1 lists complaints -> should see only 2
    res1 = await async_test_client.get("/api/v1/complaints", headers=h1)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total"] == 2
    assert len(data1["items"]) == 2

    # Admin lists complaints -> should see 3
    res_admin = await async_test_client.get("/api/v1/complaints", headers=h_admin)
    assert res_admin.status_code == 200
    data_admin = res_admin.json()
    assert data_admin["total"] == 3


@pytest.mark.asyncio
async def test_get_complaint_by_id_and_permission(async_test_client):
    user1_token = await register_and_get_token(async_test_client, "owner@example.com")
    user2_token = await register_and_get_token(async_test_client, "other@example.com")

    h1 = {"Authorization": f"Bearer {user1_token}"}
    h2 = {"Authorization": f"Bearer {user2_token}"}

    create_res = await async_test_client.post("/api/v1/complaints", json={"text": "Rude customer service agent behavior"}, headers=h1)
    cmp_data = create_res.json()
    cmp_id = cmp_data["id"]
    human_cmp_id = cmp_data["complaint_id"]

    # Owner can fetch via UUID and human ID
    res_uuid = await async_test_client.get(f"/api/v1/complaints/{cmp_id}", headers=h1)
    assert res_uuid.status_code == 200

    res_human = await async_test_client.get(f"/api/v1/complaints/{human_cmp_id}", headers=h1)
    assert res_human.status_code == 200

    # Other user gets 403 Forbidden
    res_other = await async_test_client.get(f"/api/v1/complaints/{cmp_id}", headers=h2)
    assert res_other.status_code == 403
