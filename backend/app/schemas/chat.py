from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.ticket import TicketResponse


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, json_schema_extra={"example": "I need help with my delayed package shipment."})
    session_id: str = Field(..., min_length=1, json_schema_extra={"example": "sess_892374"})


class ChatResponse(BaseModel):
    reply: str
    intent: str
    resolved: bool = False
    ticket: Optional[TicketResponse] = None
