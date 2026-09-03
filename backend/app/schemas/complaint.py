from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class ComplaintCreate(BaseModel):
    text: str = Field(..., min_length=5, json_schema_extra={"example": "Money was deducted from my account but transaction failed."})
    category: Optional[str] = Field(default=None, json_schema_extra={"example": "Billing"})
    priority: Optional[str] = Field(default=None, json_schema_extra={"example": "High"})
    complexity: Optional[str] = Field(default=None, json_schema_extra={"example": "Medium"})
    recommended_team: Optional[str] = Field(default=None, json_schema_extra={"example": "Billing Support"})


class ComplaintUpdate(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = None
    complexity: Optional[str] = None
    recommended_team: Optional[str] = None


class ComplaintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    complaint_id: str
    complaint_text: str
    category: str
    priority: str
    complexity: str
    recommended_team: str
    user_id: Optional[int] = None
    ticket_id: Optional[Union[str, int]] = None
    created_at: datetime
    updated_at: datetime


class PaginatedComplaintList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ComplaintResponse]
