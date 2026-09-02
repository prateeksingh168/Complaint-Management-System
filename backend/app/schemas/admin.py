from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserResponse


class TicketAssignRequest(BaseModel):
    agent_id: Optional[int] = Field(default=None, description="ID of target agent")
    team_id: Optional[int] = Field(default=None, description="ID of target team")


class AgentWorkloadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    skills: Optional[str] = None
    availability: str
    current_workload: int


class AdminAnalyticsResponse(BaseModel):
    total_complaints: int
    total_tickets: int
    status_counts: Dict[str, int]
    category_counts: Dict[str, int]
    priority_counts: Dict[str, int]
    avg_resolution_time_hours: Optional[float] = None
    escalated_tickets_count: int


class PaginatedUserList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[UserResponse]
