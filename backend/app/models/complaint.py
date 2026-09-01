import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.ticket import Ticket


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # e.g., CMP-10025
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="Medium")  # Urgent, High, Medium, Low
    complexity: Mapped[str] = mapped_column(String(20), nullable=False, default="Medium")  # High, Medium, Low
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Registered", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="complaints")
    category: Mapped["Category"] = relationship("Category", back_populates="complaints")
    ticket: Mapped[Optional["Ticket"]] = relationship("Ticket", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
