from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TeamInTicket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class AgentInTicket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str


class TicketCreate(BaseModel):
    complaint_id: str = Field(..., description="UUID or CMP-XXXXX of linked complaint")
    assigned_team_id: Optional[int] = None
    assigned_agent_id: Optional[str] = None
    priority: Optional[str] = Field(default="Medium")
    status: Optional[str] = Field(default="Registered")


class TicketUpdate(BaseModel):
    assigned_team_id: Optional[int] = None
    assigned_agent_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    escalated: Optional[bool] = None


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "In Progress"})
    note: Optional[str] = Field(default=None, json_schema_extra={"example": "Investigation started by agent."})


class TicketHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    old_status: Optional[str] = None
    new_status: str
    changed_by: str
    note: Optional[str] = None
    created_at: datetime


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    complaint_id: str
    assigned_team_id: Optional[int] = None
    assigned_team: Optional[TeamInTicket] = None
    assigned_agent_id: Optional[str] = None
    assigned_agent: Optional[AgentInTicket] = None
    status: str
    priority: str
    ai_confidence: Optional[float] = None
    escalated: bool
    escalated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    history: List[TicketHistoryResponse] = []


class PaginatedTicketList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TicketResponse]
