from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TicketHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    old_status: Optional[str] = None
    new_status: str
    changed_by: Optional[int] = None
    changed_at: datetime


class TicketCreate(BaseModel):
    complaint_id: str
    assigned_team_id: Optional[int] = None
    assigned_agent_id: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = "Registered"


class TicketUpdate(BaseModel):
    assigned_team_id: Optional[int] = None
    assigned_agent_id: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    escalated: Optional[bool] = None
    resolution_information: Optional[str] = None


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "In Progress"})
    note: Optional[str] = Field(default=None, json_schema_extra={"example": "Assigned to agent John"})


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    complaint_id: str
    category: str
    priority: str
    status: str
    assigned_team_id: Optional[int] = None
    assigned_agent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_information: Optional[str] = None
    history: List[TicketHistoryResponse] = []


class PaginatedTicketList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TicketResponse]
