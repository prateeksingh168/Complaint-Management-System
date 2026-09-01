import uuid
from typing import TYPE_CHECKING, Any, List
from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.team import Team
    from app.models.ticket import Ticket


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False)
    skills: Mapped[Any] = mapped_column(JSON, default=list, nullable=False)
    current_workload: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="agent_profile")
    team: Mapped["Team"] = relationship("Team", back_populates="agents")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="assigned_agent")
