from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models."""
    pass


# Import all models here so that Base.metadata has a full record of models
from app.models.user import User  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.team import Team  # noqa: F401
from app.models.agent import Agent  # noqa: F401
from app.models.complaint import Complaint  # noqa: F401
from app.models.ticket import Ticket  # noqa: F401
from app.models.ticket_history import TicketHistory  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.faq import FAQ  # noqa: F401
