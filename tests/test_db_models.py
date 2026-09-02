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
from app.models.ai_prediction import AIPrediction
from app.models.complaint import Complaint
from app.models.faq import FAQ
from app.models.notification import Notification
from app.models.team import Team
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.models.user import User


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
async def test_create_and_query_all_models(async_db_session):
    # 1. User
    user = User(name="Test User", email="user@example.com", password_hash="hash", role="user")
    async_db_session.add(user)
    await async_db_session.flush()
    assert user.id is not None

    # 2. Team & Agent
    team = Team(name="Billing Support", description="Billing inquiries")
    async_db_session.add(team)
    await async_db_session.flush()

    agent = Agent(name="Agent One", email="agent1@example.com", team_id=team.id, skills="Billing")
    async_db_session.add(agent)
    await async_db_session.flush()

    # 3. Complaint & Ticket
    complaint = Complaint(
        complaint_id="CMP-12345",
        complaint_text="Duplicate billing charge",
        category="Billing",
        priority="High",
        complexity="Medium",
        recommended_team="Billing Support",
        user_id=user.id,
    )
    async_db_session.add(complaint)
    await async_db_session.flush()

    ticket = Ticket(
        ticket_number="TKT-12345",
        complaint_id=complaint.complaint_id,
        category="Billing",
        priority="High",
        assigned_team_id=team.id,
        assigned_agent_id=agent.id,
    )
    async_db_session.add(ticket)
    await async_db_session.flush()

    # 4. Ticket History, Notification, FAQ, AI Prediction
    history = TicketHistory(ticket_id=ticket.id, old_status="Registered", new_status="In Progress", changed_by=user.id)
    notif = Notification(user_id=user.id, ticket_id=ticket.id, message="Status updated", type="status_update")
    faq = FAQ(question="How to request refund?", answer="Contact billing support", category="Billing")
    ai_pred = AIPrediction(ticket_id=ticket.id, predicted_category="Billing", predicted_priority="High", confidence_score=0.95)

    async_db_session.add_all([history, notif, faq, ai_pred])
    await async_db_session.commit()

    # Queries
    assert ticket.id is not None
    assert history.id is not None
    assert notif.id is not None
    assert faq.id is not None
    assert ai_pred.id is not None
