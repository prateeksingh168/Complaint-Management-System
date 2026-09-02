from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.team import Team
from app.models.ticket import Ticket


async def find_best_agent_for_ticket(
    db: AsyncSession,
    ticket: Ticket,
) -> Optional[Agent]:
    """
    Selects the optimal support agent based on team matching, availability, skills, and current workload.
    """
    stmt = select(Agent).where(Agent.availability == "Available")

    if ticket.assigned_team_id:
        stmt = stmt.where(Agent.team_id == ticket.assigned_team_id)

    res = await db.execute(stmt)
    available_agents = res.scalars().all()

    if not available_agents:
        # Fallback to any available agent
        fallback_res = await db.execute(select(Agent).where(Agent.availability == "Available"))
        available_agents = fallback_res.scalars().all()

    if not available_agents:
        return None

    # Score available agents
    best_agent = None
    best_score = -1.0

    category_lower = ticket.category.lower()

    for agent in available_agents:
        score = 10.0
        
        # Skill matching
        skills_str = agent.skills or ""
        if category_lower in skills_str.lower():
            score += 20.0

        # Workload penalty (lower workload gets higher score)
        score -= agent.current_workload * 2.0

        if score > best_score:
            best_score = score
            best_agent = agent

    return best_agent


async def assign_agent_or_team(
    db: AsyncSession,
    ticket: Ticket,
) -> Ticket:
    """Auto-assigns ticket to a matching Team and Agent."""
    # Find matching team if not assigned
    if not ticket.assigned_team_id:
        team_name = f"{ticket.category} Support"
        team_res = await db.execute(select(Team).where(Team.name == team_name))
        team = team_res.scalar_one_or_none()

        if not team:
            general_res = await db.execute(select(Team).where(Team.name == "General Support"))
            team = general_res.scalar_one_or_none()

        if team:
            ticket.assigned_team_id = team.id

    # Auto-assign agent
    best_agent = await find_best_agent_for_ticket(db, ticket)
    if best_agent:
        ticket.assigned_agent_id = best_agent.id
        best_agent.current_workload += 1

    return ticket
