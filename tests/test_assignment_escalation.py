import sys
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure backend directory is in sys.path
backend_path = str(Path(__file__).resolve().parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.base import Base
from app.models.agent import Agent
from app.models.complaint import Complaint
from app.models.team import Team
from app.models.ticket import Ticket
from app.services.assignment_service import assign_agent_or_team


@pytest_asyncio.fixture
async def async_db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSession() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_agent_auto_assignment_logic(async_db_session):
    # Seed Team & Agent
    team = Team(name="Billing Support")
    async_db_session.add(team)
    await async_db_session.commit()

    agent1 = Agent(name="Billing Agent 1", email="b1@example.com", team_id=team.id, skills="Billing", availability="Available", current_workload=5)
    agent2 = Agent(name="Billing Agent 2", email="b2@example.com", team_id=team.id, skills="Billing", availability="Available", current_workload=1)
    async_db_session.add_all([agent1, agent2])
    await async_db_session.commit()

    # Create Complaint & Ticket
    complaint = Complaint(
        complaint_id="CMP-99001",
        complaint_text="Billing refund inquiry",
        category="Billing",
        priority="High",
        complexity="Medium",
        recommended_team="Billing Support",
    )
    async_db_session.add(complaint)
    await async_db_session.flush()

    ticket = Ticket(
        ticket_number="TKT-99001",
        complaint_id="CMP-99001",
        category="Billing",
        priority="High",
        status="Registered",
    )
    async_db_session.add(ticket)
    await async_db_session.flush()

    # Run Auto Assignment
    assigned_ticket = await assign_agent_or_team(async_db_session, ticket)
    assert assigned_ticket.assigned_team_id == team.id
    # Agent 2 has lower workload (1 vs 5), so Agent 2 should be selected
    assert assigned_ticket.assigned_agent_id == agent2.id
    assert agent2.current_workload == 2
