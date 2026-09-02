from typing import Optional, Union
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse, PaginatedNotificationList


async def create_notification(
    db: AsyncSession,
    user_id: int,
    message: str,
    ticket_id: Optional[int] = None,
    notif_type: str = "info",
) -> Notification:
    notif = Notification(
        user_id=user_id,
        ticket_id=ticket_id,
        message=message,
        type=notif_type,
        is_read=False,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif


async def get_user_notifications(
    db: AsyncSession,
    current_user: User,
    page: int = 1,
    page_size: int = 10,
    unread_only: bool = False,
) -> PaginatedNotificationList:
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    stmt = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
    items_res = await db.execute(stmt)
    notifications = items_res.scalars().all()

    return PaginatedNotificationList(
        total=total,
        page=page,
        page_size=page_size,
        items=[NotificationResponse.model_validate(n) for n in notifications],
    )


async def mark_notification_as_read(
    db: AsyncSession,
    notification_id: Union[int, str],
    current_user: User,
) -> Notification:
    try:
        notif_id = int(notification_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid notification ID format")

    stmt = select(Notification).where(Notification.id == notif_id)
    res = await db.execute(stmt)
    notif = res.scalar_one_or_none()

    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this notification")

    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return notif
