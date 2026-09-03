from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticket_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tickets.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(30), default="status_update", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="notifications")
    ticket: Mapped[Optional["Ticket"]] = relationship("Ticket", back_populates="notifications")
