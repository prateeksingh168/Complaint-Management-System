import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
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
        cats = [
            Category(name="Other", is_active=True),
            Category(name="Billing", is_active=True),
            Category(name="Delivery", is_active=True),
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


@pytest.mark.asyncio
async def test_chat_relay_general_inquiry(async_test_client):
    mock_ai_chat = {
        "reply": "Our business hours are 9 AM to 6 PM.",
        "intent": "general_info",
        "resolved": True,
        "extracted_complaint": None,
    }

    with patch("app.services.ai_client.relay_chat", new_callable=AsyncMock) as mock_relay:
        mock_relay.return_value = mock_ai_chat

        payload = {"message": "What are your business hours?", "session_id": "sess_101"}
        response = await async_test_client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Our business hours are 9 AM to 6 PM."
        assert data["intent"] == "general_info"
        assert data["resolved"] is True
        assert data["ticket"] is None


@pytest.mark.asyncio
async def test_chat_relay_extracted_complaint_creates_ticket(async_test_client):
    mock_ai_chat = {
        "reply": "I understand your delivery was delayed. I have logged a support ticket for you.",
        "intent": "complaint",
        "resolved": False,
        "extracted_complaint": "Delivery package #99238 was delayed by 5 days",
    }

    with patch("app.services.ai_client.relay_chat", new_callable=AsyncMock) as mock_relay:
        mock_relay.return_value = mock_ai_chat

        payload = {"message": "My package #99238 is missing!", "session_id": "sess_102"}
        response = await async_test_client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "complaint"
        assert data["ticket"] is not None
        assert data["ticket"]["ticket_id"].startswith("CMP-")
