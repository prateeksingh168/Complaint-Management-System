from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryInComplaint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ComplaintCreate(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000, json_schema_extra={"example": "I was charged twice for order #12345."})
    category_id: Optional[int] = Field(default=None, description="Optional manual category override")
    priority: Optional[str] = Field(default=None, description="Optional manual priority override")
    complexity: Optional[str] = Field(default=None, description="Optional manual complexity override")


class ComplaintUpdate(BaseModel):
    text: Optional[str] = Field(default=None, min_length=5, max_length=5000)
    category_id: Optional[int] = None
    priority: Optional[str] = None
    complexity: Optional[str] = None
    status: Optional[str] = None


class ComplaintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    complaint_id: str
    user_id: str
    text: str
    category_id: int
    category: Optional[CategoryInComplaint] = None
    priority: str
    complexity: str
    status: str
    created_at: datetime
    updated_at: datetime
    ticket_id: Optional[str] = None


class PaginatedComplaintList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ComplaintResponse]
