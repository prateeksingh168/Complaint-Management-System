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


@pytest_asyncio.fixture
async def async_test_client():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_register_user_success(async_test_client):
    payload = {
        "name": "Jane User",
        "email": "jane@example.com",
        "password": "Password123!",
        "role": "user"
    }
    response = await async_test_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["name"] == "Jane User"
    assert data["user"]["role"] == "user"
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


@pytest.mark.asyncio
async def test_register_duplicate_email(async_test_client):
    payload = {
        "name": "Duplicate User",
        "email": "dup@example.com",
        "password": "Password123!"
    }
    resp1 = await async_test_client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await async_test_client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 400
    res_data = resp2.json()
    error_msg = res_data.get("error", {}).get("message") or res_data.get("detail", "")
    assert "already exists" in error_msg


@pytest.mark.asyncio
async def test_login_and_profile_flow(async_test_client):
    # 1. Register
    reg_payload = {
        "name": "Login User",
        "email": "login@example.com",
        "password": "SecurePassword123!"
    }
    await async_test_client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Login
    login_payload = {
        "email": "login@example.com",
        "password": "SecurePassword123!"
    }
    login_resp = await async_test_client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 3. Access Profile
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_resp = await async_test_client.get("/api/v1/auth/profile", headers=headers)
    assert profile_resp.status_code == 200
    profile_data = profile_resp.json()
    assert profile_data["email"] == "login@example.com"

    # 4. Refresh Token
    refresh_resp = await async_test_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert "access_token" in new_tokens


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_test_client):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword"
    }
    response = await async_test_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    res_data = response.json()
    error_msg = res_data.get("error", {}).get("message") or res_data.get("detail", "")
    assert "Incorrect email or password" in error_msg


@pytest.mark.asyncio
async def test_profile_unauthorized_without_token(async_test_client):
    response = await async_test_client.get("/api/v1/auth/profile")
    assert response.status_code in (401, 403)
