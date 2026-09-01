import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.team import Team
    from app.models.agent import Agent
    from app.models.ticket_history import TicketHistory
    from app.models.notification import Notification


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # e.g., CMP-10025
    complaint_id: Mapped[str] = mapped_column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), unique=True, nullable=False)
    assigned_team_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Registered", index=True)  # Registered, In Progress, Under Review, Resolved
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="Medium", index=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    escalated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    complaint: Mapped["Complaint"] = relationship("Complaint", back_populates="ticket")
    assigned_team: Mapped[Optional["Team"]] = relationship("Team", back_populates="tickets")
    assigned_agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="tickets")
    history: Mapped[List["TicketHistory"]] = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketHistory.created_at.desc()")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="ticket", cascade="all, delete-orphan")
