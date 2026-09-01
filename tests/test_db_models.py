import sys
from pathlib import Path
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure backend directory is in sys.path
backend_path = str(Path(__file__).resolve().parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.base import Base
from app.models.user import User
from app.models.category import Category
from app.models.team import Team
from app.models.agent import Agent
from app.models.complaint import Complaint
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.models.notification import Notification
from app.models.faq import FAQ


def test_metadata_tables_registered():
    """Verify that all 9 ORM models are registered in Base.metadata."""
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
    assert expected_tables.issubset(table_names)


@pytest.mark.asyncio
async def test_in_memory_db_schema_creation_and_seeding():
    """Verify in-memory SQLite schema creation and basic model operations."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSession() as session:
        # Create Category & Team
        cat = Category(name="Technical", is_active=True)
        team = Team(name="Technical Support", is_active=True)
        session.add_all([cat, team])
        await session.commit()
        await session.refresh(cat)
        await session.refresh(team)

        assert cat.id is not None
        assert team.id is not None

        # Create User & Agent
        user = User(
            name="John Agent",
            email="john.agent@example.com",
            password_hash="hashed_pw_secret",
            role="agent",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        agent = Agent(
            user_id=user.id,
            team_id=team.id,
            skills=["Technical", "Troubleshooting"],
            current_workload=0,
            is_available=True,
        )
        session.add(agent)
        await session.commit()
        await session.refresh(agent)

        assert agent.id is not None
        assert agent.team_id == team.id

        # Create Complaint
        complaint = Complaint(
            complaint_id="CMP-10001",
            user_id=user.id,
            text="Internet disconnects frequently",
            category_id=cat.id,
            priority="High",
            complexity="Medium",
            status="Registered",
        )
        session.add(complaint)
        await session.commit()
        await session.refresh(complaint)

        # Create Ticket
        ticket = Ticket(
            ticket_id="CMP-10001",
            complaint_id=complaint.id,
            assigned_team_id=team.id,
            assigned_agent_id=agent.id,
            status="Registered",
            priority="High",
            ai_confidence=0.95,
        )
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)

        assert ticket.id is not None
        assert ticket.assigned_agent_id == agent.id

    await test_engine.dispose()
