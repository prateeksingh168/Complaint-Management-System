from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserResponse


class TicketAssignRequest(BaseModel):
    agent_id: Optional[str] = Field(default=None, description="UUID of target agent")
    team_id: Optional[int] = Field(default=None, description="ID of target team")


class AgentWorkloadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    user_name: str
    user_email: str
    team_id: int
    team_name: str
    skills: List[str]
    current_workload: int
    is_available: bool


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
