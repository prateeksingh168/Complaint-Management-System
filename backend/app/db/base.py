from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models."""
    pass


# Import all ORM models so Base.metadata is fully populated and mappers resolve correctly
import app.models  # noqa: F401
