import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
import httpx
import pytest

# Ensure backend directory is in sys.path
backend_path = str(Path(__file__).resolve().parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services import ai_client


@pytest.mark.asyncio
async def test_classify_complaint_ai_success():
    mock_response = httpx.Response(
        status_code=200,
        json={"category": "Billing", "priority": "High", "confidence": 0.95},
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        res = await ai_client.classify_complaint("I was billed twice")
        assert res["category"] == "Billing"
        assert res["priority"] == "High"
        assert res["confidence"] == 0.95


@pytest.mark.asyncio
async def test_classify_complaint_timeout_fallback():
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timeout")):
        res = await ai_client.classify_complaint("I need a refund for my billing error")
        assert res["category"] == "Billing"
        assert res["confidence"] is None


@pytest.mark.asyncio
async def test_relay_chat_ai_success():
    mock_response = httpx.Response(
        status_code=200,
        json={
            "reply": "How can I help you with your account?",
            "intent": "account_help",
            "resolved": False,
            "extracted_complaint": None,
        },
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        res = await ai_client.relay_chat("I cannot login", "session-123")
        assert res["reply"] == "How can I help you with your account?"
        assert res["intent"] == "account_help"
        assert res["resolved"] is False


@pytest.mark.asyncio
async def test_relay_chat_fallback_on_error():
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        res = await ai_client.relay_chat("Hello", "session-456")
        assert "currently offline" in res["reply"]
        assert res["intent"] == "general"
        assert res["resolved"] is False
