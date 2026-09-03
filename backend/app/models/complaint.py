from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    complaint_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # Billing, Technical, Service, Account, Delivery, Other
    priority: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # Urgent, High, Medium, Low
    complexity: Mapped[str] = mapped_column(String(20), default="Medium", nullable=False, index=True)  # Low, Medium, High
    recommended_team: Mapped[str] = mapped_column(String(100), default="General Support", nullable=False, index=True)

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="complaints")
    ticket: Mapped[Optional["Ticket"]] = relationship("Ticket", back_populates="complaint", uselist=False)
