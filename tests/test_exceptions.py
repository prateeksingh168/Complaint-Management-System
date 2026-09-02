import sys
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Ensure backend directory is in sys.path
backend_path = str(Path(__file__).resolve().parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app


@pytest_asyncio.fixture
async def async_test_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_validation_error_envelope(async_test_client):
    # Invalid registration payload (missing required fields)
    response = await async_test_client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"]["details"], list)


@pytest.mark.asyncio
async def test_unauthorized_error_envelope(async_test_client):
    # Invalid Bearer token
    headers = {"Authorization": "Bearer invalid_token"}
    response = await async_test_client.get("/api/v1/auth/profile", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_401"
