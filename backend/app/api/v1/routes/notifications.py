from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse, PaginatedNotificationList
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=PaginatedNotificationList, status_code=status.HTTP_200_OK, summary="List Notifications")
async def list_notifications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    unread_only: bool = Query(default=False, description="Filter unread notifications only"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a paginated list of notifications for the authenticated user.
    """
    return await notification_service.get_user_notifications(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
        unread_only=unread_only,
    )


@router.put("/{id}/read", response_model=NotificationResponse, status_code=status.HTTP_200_OK, summary="Mark Notification Read")
async def mark_read(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Marks a specific notification as read.
    """
    notif = await notification_service.mark_notification_as_read(db, id, current_user)
    return NotificationResponse.model_validate(notif)
