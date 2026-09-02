from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("teams.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    availability: Mapped[str] = mapped_column(String(20), default="Available", nullable=False)  # 'Available', 'Busy', 'Unavailable'
    current_workload: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="agents")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="assigned_agent")
