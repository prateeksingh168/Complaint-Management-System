import sys
from pathlib import Path
import pytest
from sqlalchemy.orm import configure_mappers

# Ensure backend directory is in sys.path
backend_path = str(Path(__file__).resolve().parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.base import Base


def test_all_orm_mappers_configure_without_explicit_model_imports():
    """
    Regression test verifying that all 9 SQLAlchemy ORM mappers (including FAQ and Category relationships)
    are automatically registered via app.db.base / app.models without relying on test modules explicitly importing models.
    """
    # Force configure_mappers() which validates all string relationship names like 'FAQ', 'Category', etc.
    configure_mappers()

    table_names = set(Base.metadata.tables.keys())
    expected_tables = {
        "users",
        "categories",
        "teams",
        "agents",
        "complaints",
        "tickets",
        "ticket_history",
        "notifications",
        "faqs",
    }
    assert expected_tables.issubset(table_names), f"Missing tables in metadata: {expected_tables - table_names}"
