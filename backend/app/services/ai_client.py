from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.core.logging import logger


def rule_based_fallback(text: str) -> Dict[str, Any]:
    """Rule-based keyword fallback classification when AI service is unavailable."""
    text_lower = text.lower()

    category = "Other"
    priority = "Medium"

    if any(
        k in text_lower
        for k in [
            "bill",
            "invoice",
            "charge",
            "refund",
            "payment",
            "price",
            "cost",
            "fee",
        ]
    ):
        category = "Billing"
        priority = (
            "High"
            if "charge" in text_lower or "fraud" in text_lower
            else "Medium"
        )

    elif any(
        k in text_lower
        for k in [
            "deliver",
            "ship",
            "tracking",
            "package",
            "delay",
            "courier",
            "order",
        ]
    ):
        category = "Delivery"
        priority = "Medium"

    elif any(
        k in text_lower
        for k in [
            "tech",
            "bug",
            "crash",
            "error",
            "server",
            "disconnect",
            "slow",
            "down",
        ]
    ):
        category = "Technical"
        priority = (
            "High"
            if "crash" in text_lower or "down" in text_lower
            else "Medium"
        )

    elif any(
        k in text_lower
        for k in [
            "account",
            "login",
            "password",
            "sign",
            "auth",
            "profile",
        ]
    ):
        category = "Account"
        priority = (
            "High"
            if "password" in text_lower or "auth" in text_lower
            else "Medium"
        )

    elif any(
        k in text_lower
        for k in [
            "service",
            "agent",
            "support",
            "staff",
            "behavior",
            "rude",
        ]
    ):
        category = "Service"
        priority = "Medium"

    if any(
        k in text_lower
        for k in [
            "urgent",
            "immediately",
            "critical",
            "emergency",
            "hacked",
        ]
    ):
        priority = "Urgent"

    return {
        "category": category,
        "priority": priority,
        "confidence": None,
    }


def chat_fallback(message: str) -> Dict[str, Any]:
    """Fallback response generator for chatbot relay when AI service is offline."""
    return {
        "reply": (
            "Thank you for reaching out. Our automated assistant is "
            "currently offline, but your inquiry has been logged. "
            "You may submit a complaint directly if you need immediate support."
        ),
        "intent": "general",
        "resolved": False,
        "extracted_complaint": None,
        "ticket": None,
    }


async def classify_complaint(
    complaint_text: str,
) -> Dict[str, Any]:
    """
    Calls AI service endpoint POST {AI_SERVICE_URL}/classify.

    Falls back to keyword rule-based classification if AI is
    offline or times out.
    """

    url = (
        f"{settings.AI_SERVICE_URL.rstrip('/')}"
        "/classify"
    )

    payload = {
        "complaint_text": complaint_text
    }

    try:
        async with httpx.AsyncClient(
            timeout=settings.AI_REQUEST_TIMEOUT_SECONDS
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            if response.status_code == 200:

                data = response.json()

                return {
                    "category": data.get(
                        "category",
                        "Other",
                    ),
                    "priority": data.get(
                        "priority",
                        "Medium",
                    ),
                    "complexity": data.get(
                        "complexity"
                    ),
                    "recommended_team": data.get(
                        "recommended_team"
                    ),
                    "confidence": (
                        float(data.get("confidence", 1.0))
                        if data.get("confidence") is not None
                        else None
                    ),
                    "ticket": data.get("ticket"),
                }

            else:

                logger.warning(
                    "AI classification service returned "
                    f"HTTP status code {response.status_code}. "
                    "Using fallback."
                )

    except Exception as exc:

        logger.warning(
            "AI classification service call failed "
            f"or timed out: {exc}. "
            "Using rule-based fallback."
        )

    return rule_based_fallback(
        complaint_text
    )


async def relay_chat(
    message: str,
    session_id: str,
) -> Dict[str, Any]:
    """
    Relays chat messages to AI service endpoint POST
    {AI_SERVICE_URL}/chat.

    The complete AI ticket object is preserved so that
    complexity and recommended_team are available to the
    backend chatbot route and frontend.
    """

    url = (
        f"{settings.AI_SERVICE_URL.rstrip('/')}"
        "/chat"
    )

    payload = {
        "message": message,
        "session_id": session_id,
    }

    try:

        async with httpx.AsyncClient(
            timeout=settings.AI_REQUEST_TIMEOUT_SECONDS
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            if response.status_code == 200:

                data = response.json()

                return {
                    "reply": data.get(
                        "reply",
                        "No response generated.",
                    ),
                    "intent": data.get(
                        "intent",
                        "general",
                    ),
                    "resolved": bool(
                        data.get(
                            "resolved",
                            False,
                        )
                    ),
                    "extracted_complaint": data.get(
                        "extracted_complaint"
                    ),

                    # IMPORTANT:
                    # Preserve complete AI ticket data.
                    "ticket": data.get(
                        "ticket"
                    ),
                }

            else:

                logger.warning(
                    "AI chat service returned "
                    f"HTTP status code {response.status_code}. "
                    "Using fallback."
                )

    except Exception as exc:

        logger.warning(
            "AI chat service call failed "
            f"or timed out: {exc}. "
            "Using chatbot fallback."
        )

    return chat_fallback(message)