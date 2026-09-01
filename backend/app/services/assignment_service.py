from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.agent import Agent
from app.models.complaint import Complaint
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory


def calculate_agent_score(
    agent: Agent,
    ticket: Ticket,
    complaint: Complaint,
    category_name: str,
    max_workload: int,
) -> float:
    """Calculates weighted assignment score for an agent based on PRD Section 10 formula."""
    # 1. Skill match
    agent_skills = agent.skills if isinstance(agent.skills, list) else []
    skills_lower = [str(s).lower() for s in agent_skills]
    complaint_text_lower = complaint.text.lower()
    cat_lower = category_name.lower()

    skill_match = 1.0 if any(s in complaint_text_lower or s in cat_lower for s in skills_lower) else 0.0

    # 2. Availability
    avail_score = 1.0 if agent.is_available else 0.0

    # 3. Workload (normalized 0 to 1)
    norm_workload = (agent.current_workload / max(max_workload, 1)) if max_workload > 0 else 0.0
    workload_score = max(0.0, 1.0 - norm_workload)

    # 4. Category match
    cat_match = 1.0 if any(s in cat_lower for s in skills_lower) else 0.5

    # 5. Priority score
    priority_map = {"Urgent": 1.0, "High": 0.75, "Medium": 0.5, "Low": 0.25}
    priority_score = priority_map.get(ticket.priority, 0.5)

    score = (
        settings.SKILL_MATCH_WEIGHT * skill_match
        + settings.AVAILABILITY_WEIGHT * avail_score
        + settings.WORKLOAD_WEIGHT * workload_score
        + settings.CATEGORY_MATCH_WEIGHT * cat_match
        + settings.PRIORITY_WEIGHT * priority_score
    )

    return round(score, 4)


async def auto_assign_ticket(db: AsyncSession, ticket_id: str) -> Optional[Agent]:
    """
    Finds the highest scoring available agent in the assigned team and assigns the ticket.
    Increments agent workload and transitions ticket status to 'In Progress'.
    """
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.complaint).selectinload(Complaint.category), selectinload(Ticket.history))
        .where((Ticket.id == ticket_id) | (Ticket.ticket_id == ticket_id))
    )
    res = await db.execute(stmt)
    ticket = res.scalar_one_or_none()

    if not ticket:
        return None

    complaint = ticket.complaint
    category_name = complaint.category.name if complaint and complaint.category else "Other"

    # Query candidate agents in assigned team
    agent_stmt = select(Agent).options(selectinload(Agent.user), selectinload(Agent.team))
    if ticket.assigned_team_id:
        agent_stmt = agent_stmt.where(Agent.team_id == ticket.assigned_team_id)

    agent_res = await db.execute(agent_stmt)
    candidates: List[Agent] = agent_res.scalars().all()

    # Filter available candidates
    available_candidates = [a for a in candidates if a.is_available]
    if not available_candidates:
        # Fallback to all candidates if none currently marked available
        available_candidates = candidates

    if not available_candidates:
        return None

    max_workload = max((a.current_workload for a in available_candidates), default=1)

    best_agent: Optional[Agent] = None
    best_score: float = -1.0

    for agent in available_candidates:
        score = calculate_agent_score(agent, ticket, complaint, category_name, max_workload)
        if score > best_score:
            best_score = score
            best_agent = agent

    if best_agent:
        old_status = ticket.status
        ticket.assigned_agent_id = best_agent.id
        ticket.assigned_team_id = best_agent.team_id
        best_agent.current_workload += 1

        if ticket.status == "Registered":
            ticket.status = "In Progress"
            if complaint:
                complaint.status = "In Progress"

        # Log history row
        history = TicketHistory(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=ticket.status,
            changed_by=best_agent.user_id,
            note=f"Auto-assigned to agent {best_agent.user.name} (score: {best_score:.4f})",
        )
        db.add(history)
        ticket.history.insert(0, history)

        await db.commit()
        await db.refresh(best_agent)
        return best_agent

    return None
