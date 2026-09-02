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

router = APIRouter(prefix="/chat", tags=["Chatbot Relay"])


async def get_optional_user(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Helper to extract user if valid Authorization header present, else None for guest."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id:
            res = await db.execute(select(User).where(User.id == user_id))
            return res.scalar_one_or_none()
    except Exception:
        pass
    return None


async def get_or_create_guest_user(db: AsyncSession) -> User:
    """Helper to fetch or create a default guest user for unauthenticated chat complaints."""
    guest_email = "guest.user@system.local"
    res = await db.execute(select(User).where(User.email == guest_email))
    guest = res.scalar_one_or_none()
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


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK, summary="Chatbot Relay Endpoint")
async def chat_relay(
    chat_in: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Forwards user message and session_id to the AI module chat endpoint.
    If the AI module decides a complaint ticket is needed or extracts a complaint text,
    it automatically persists the complaint and linked ticket, returning ticket details in the response payload.
    Supports guest sessions and logged-in user sessions.
    """
    ai_result = await ai_client.relay_chat(chat_in.message, chat_in.session_id)

    reply = ai_result.get("reply", "Thank you for your message.")
    intent = ai_result.get("intent", "general")
    resolved = bool(ai_result.get("resolved", False))
    extracted_complaint = ai_result.get("extracted_complaint")

    ticket_response: Optional[TicketResponse] = None

    # If AI extracted a complaint or intent demands complaint registration
    if extracted_complaint or intent in ["complaint", "create_ticket", "ticket_request"]:
        complaint_text = extracted_complaint or chat_in.message
        acting_user = current_user or await get_or_create_guest_user(db)

        complaint = await complaint_service.create_complaint(
            db=db,
            user_id=acting_user.id,
            complaint_in=ComplaintCreate(text=complaint_text),
        )

        if complaint.ticket:
            t = await ticket_service.get_ticket_by_id(db, complaint.ticket.id, acting_user, check_permission=False)
            ticket_response = TicketResponse.model_validate(t)

    return ChatResponse(
        reply=reply,
        intent=intent,
        resolved=resolved,
        ticket=ticket_response,
    )
