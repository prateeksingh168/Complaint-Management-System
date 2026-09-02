from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    complaint_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("complaints.complaint_id", onupdate="CASCADE", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="Registered", nullable=False, index=True)

    assigned_team_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("teams.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_agent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("agents.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
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
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_information: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="ticket")
    assigned_team: Mapped[Optional["Team"]] = relationship("Team", back_populates="tickets")
    assigned_agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="tickets")
    history: Mapped[List["TicketHistory"]] = relationship(
        "TicketHistory",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketHistory.changed_at.desc()",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )
    ai_predictions: Mapped[List["AIPrediction"]] = relationship(
        "AIPrediction",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )
