from typing import TYPE_CHECKING, List
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.ticket import Ticket


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    agents: Mapped[List["Agent"]] = relationship("Agent", back_populates="team")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="assigned_team")
