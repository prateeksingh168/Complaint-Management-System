from typing import Optional

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.complaint import ComplaintCreate
from app.schemas.ticket import TicketResponse
from app.services import ai_client, complaint_service, ticket_service
from app.core.logging import logger


router = APIRouter(prefix="/chat", tags=["Chatbot Relay"])


async def get_optional_user(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Return the authenticated user when a valid Bearer access token
    is supplied.
    """

    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.split(" ", 1)[1].strip()

    if not token:
        return None

    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            return None

        user_id = int(payload.get("sub"))

        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if user is None:
            return None

        return user

    except Exception as exc:
        logger.exception(
            "Optional chatbot authentication failed: %s",
            exc,
        )

        await db.rollback()

        return None


async def get_or_create_guest_user(db: AsyncSession) -> User:
    """
    Fetch or create a default guest user for unauthenticated
    chatbot complaints.
    """

    guest_email = "guest.user@system.local"

    result = await db.execute(
        select(User).where(User.email == guest_email)
    )

    guest = result.scalar_one_or_none()

    if not guest:
        guest = User(
            name="Guest User",
            email=guest_email,
            password_hash="guest_no_login",
            role="user",
        )

        db.add(guest)
        await db.commit()
        await db.refresh(guest)

    return guest


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chatbot Relay Endpoint",
)
async def chat_relay(
    chat_in: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Forward the user's message and session ID to the AI service.

    If the AI service identifies the message as a complaint,
    the complaint and linked ticket are persisted in the database.

    Supports both authenticated users and guest sessions.
    """

    # ---------------------------------------------------------
    # 1. Send message to AI service
    # ---------------------------------------------------------
    ai_result = await ai_client.relay_chat(
        chat_in.message,
        chat_in.session_id,
    )

    reply = ai_result.get(
        "reply",
        "Thank you for your message.",
    )

    intent = ai_result.get(
        "intent",
        "general",
    )

    resolved = bool(
        ai_result.get(
            "resolved",
            False,
        )
    )

    extracted_complaint = ai_result.get(
        "extracted_complaint"
    )

    ticket_response: Optional[TicketResponse] = None

    # ---------------------------------------------------------
    # 2. Create complaint when AI identifies one
    # ---------------------------------------------------------
    if (
        extracted_complaint
        or intent in [
            "complaint",
            "create_ticket",
            "ticket_request",
        ]
    ):
        complaint_text = (
            extracted_complaint
            or chat_in.message
        )

        # Use authenticated user when available.
        # Otherwise use the system guest user.
        acting_user = (
            current_user
            or await get_or_create_guest_user(db)
        )

        # -----------------------------------------------------
        # 3. Persist complaint + linked ticket
        # -----------------------------------------------------
        complaint = await complaint_service.create_complaint(
            db=db,
            user_id=acting_user.id,
            complaint_in=ComplaintCreate(
                text=complaint_text
            ),
        )

        # -----------------------------------------------------
        # 4. Return created ticket details
        # -----------------------------------------------------
        if complaint.ticket:
            ticket = await ticket_service.get_ticket_by_id(
                db,
                complaint.ticket.id,
                acting_user,
                check_permission=False,
            )

            ticket_response = TicketResponse.model_validate(ticket)

            # Preserve AI classification details in chatbot response
            ai_ticket = ai_result.get("ticket") or {}

            ticket_response = ticket_response.model_copy(
                update={
                    "complexity": ai_ticket.get("complexity"),
                    "recommended_team": ai_ticket.get("recommended_team"),
                }
            )

           
            

    # ---------------------------------------------------------
    # 5. Return chatbot response
    # ---------------------------------------------------------
    return ChatResponse(
        reply=reply,
        intent=intent,
        resolved=resolved,
        ticket=ticket_response,
    )
