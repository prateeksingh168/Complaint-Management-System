from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    ticket_id: Optional[int] = None
    message: str
    type: str
    is_read: bool
    created_at: datetime


class PaginatedNotificationList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[NotificationResponse]
