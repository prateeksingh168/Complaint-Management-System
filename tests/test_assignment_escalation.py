from datetime import datetime, timedelta, timezone
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
from app.models.category import Category
from app.models.complaint import Complaint
from app.models.team import Team
from app.models.ticket import Ticket
from app.models.user import User
from app.services import assignment_service, escalation_service


@pytest_asyncio.fixture
async def db_session():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSession() as session:
        yield session

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_auto_assignment_logic(db_session: AsyncSession):
    # 1. Setup Category and Team
    cat = Category(name="Billing", is_active=True)
    team = Team(name="Billing Support", is_active=True)
    db_session.add_all([cat, team])
    await db_session.commit()

    # 2. Setup 2 Agents
    u1 = User(name="Agent Low Workload", email="a1@example.com", password_hash="hash", role="agent")
    u2 = User(name="Agent High Workload", email="a2@example.com", password_hash="hash", role="agent")
    db_session.add_all([u1, u2])
    await db_session.commit()

    a1 = Agent(user_id=u1.id, team_id=team.id, skills=["Billing", "Invoice"], current_workload=1, is_available=True)
    a2 = Agent(user_id=u2.id, team_id=team.id, skills=["Billing"], current_workload=5, is_available=True)
    db_session.add_all([a1, a2])
    await db_session.commit()

    # 3. Create Complaint and Ticket
    u_customer = User(name="Customer", email="c@example.com", password_hash="hash", role="user")
    db_session.add(u_customer)
    await db_session.commit()

    cmp = Complaint(complaint_id="CMP-99001", user_id=u_customer.id, text="Billing charge issue", category_id=cat.id, priority="High")
    db_session.add(cmp)
    await db_session.commit()

    ticket = Ticket(ticket_id="CMP-99001", complaint_id=cmp.id, assigned_team_id=team.id, status="Registered", priority="High")
    db_session.add(ticket)
    await db_session.commit()

    # 4. Perform Auto-Assignment
    assigned_agent = await assignment_service.auto_assign_ticket(db_session, ticket.id)

    assert assigned_agent is not None
    assert assigned_agent.id == a1.id  # Lower workload + better skill match
    assert assigned_agent.current_workload == 2

    # Verify ticket state updated
    await db_session.refresh(ticket)
    assert ticket.assigned_agent_id == a1.id
    assert ticket.status == "In Progress"


@pytest.mark.asyncio
async def test_escalation_service(db_session: AsyncSession):
    cat = Category(name="Technical", is_active=True)
    u_customer = User(name="Customer", email="c2@example.com", password_hash="hash", role="user")
    db_session.add_all([cat, u_customer])
    await db_session.commit()

    cmp = Complaint(complaint_id="CMP-99002", user_id=u_customer.id, text="Urgent server outage", category_id=cat.id, priority="Urgent")
    db_session.add(cmp)
    await db_session.commit()

    # Create ticket created 3 hours ago (Urgent SLA = 2h)
    three_hours_ago = datetime.now(timezone.utc) - timedelta(hours=3)
    ticket = Ticket(
        ticket_id="CMP-99002",
        complaint_id=cmp.id,
        status="In Progress",
        priority="Urgent",
        created_at=three_hours_ago,
        escalated=False,
    )
    db_session.add(ticket)
    await db_session.commit()

    # Run Escalation Check
    escalated_list = await escalation_service.check_and_escalate_tickets(db_session)

    assert len(escalated_list) == 1
    assert escalated_list[0].id == ticket.id
    assert escalated_list[0].escalated is True
    assert escalated_list[0].escalated_at is not None
