from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    ticket_id: Optional[str] = None
    message: str
    is_read: bool
    created_at: datetime


class PaginatedNotificationList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[NotificationResponse]
