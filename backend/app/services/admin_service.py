from typing import Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agent import Agent
from app.models.complaint import Complaint
from app.models.team import Team
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.models.user import User
from app.schemas.admin import AdminAnalyticsResponse, AgentWorkloadResponse, PaginatedUserList, TicketAssignRequest
from app.schemas.user import UserResponse
from app.services import ticket_service


async def get_analytics(db: AsyncSession) -> AdminAnalyticsResponse:
    complaint_count = (await db.execute(select(func.count(Complaint.complaint_id)))).scalar() or 0
    ticket_count = (await db.execute(select(func.count(Ticket.id)))).scalar() or 0

    status_stmt = select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
    status_res = await db.execute(status_stmt)
    status_counts: Dict[str, int] = {r[0]: r[1] for r in status_res.all()}

    cat_stmt = select(Complaint.category, func.count(Complaint.complaint_id)).group_by(Complaint.category)
    cat_res = await db.execute(cat_stmt)
    category_counts: Dict[str, int] = {r[0]: r[1] for r in cat_res.all()}

    prio_stmt = select(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority)
    prio_res = await db.execute(prio_stmt)
    priority_counts: Dict[str, int] = {r[0]: r[1] for r in prio_res.all()}

    resolved_tickets_stmt = select(Ticket).where(Ticket.status == "Resolved", Ticket.resolved_at.is_not(None))
    resolved_res = await db.execute(resolved_tickets_stmt)
    resolved_tickets = resolved_res.scalars().all()

    avg_resolution_time: Optional[float] = None
    if resolved_tickets:
        durations = []
        for t in resolved_tickets:
            if t.resolved_at and t.created_at:
                diff = (t.resolved_at - t.created_at).total_seconds() / 3600.0
                durations.append(max(0.0, diff))
        if durations:
            avg_resolution_time = round(sum(durations) / len(durations), 2)

    return AdminAnalyticsResponse(
        total_complaints=complaint_count,
        total_tickets=ticket_count,
        status_counts=status_counts,
        category_counts=category_counts,
        priority_counts=priority_counts,
        avg_resolution_time_hours=avg_resolution_time,
        escalated_tickets_count=0,
    )


async def get_users(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    role_filter: Optional[str] = None,
) -> PaginatedUserList:
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    stmt = select(User)
    if role_filter:
        stmt = stmt.where(User.role == role_filter)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    users = (await db.execute(stmt)).scalars().all()

    return PaginatedUserList(
        total=total,
        page=page,
        page_size=page_size,
        items=[UserResponse.model_validate(u) for u in users],
    )


async def get_agents_with_workload(db: AsyncSession) -> List[AgentWorkloadResponse]:
    stmt = select(Agent).options(selectinload(Agent.team))
    res = await db.execute(stmt)
    agents = res.scalars().all()

    items = []
    for a in agents:
        items.append(
            AgentWorkloadResponse(
                id=a.id,
                name=a.name,
                email=a.email,
                team_id=a.team_id,
                team_name=a.team.name if a.team else "Unassigned",
                skills=a.skills,
                availability=a.availability,
                current_workload=a.current_workload,
            )
        )
    return items


async def assign_ticket(
    db: AsyncSession,
    ticket_id: str,
    assign_in: TicketAssignRequest,
    current_user: User,
) -> Ticket:
    ticket = await ticket_service.get_ticket_by_id(db, ticket_id, current_user, check_permission=False)

    if assign_in.agent_id is not None:
        agent_res = await db.execute(select(Agent).where(Agent.id == assign_in.agent_id))
        agent = agent_res.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        
        ticket.assigned_agent_id = agent.id
        if agent.team_id:
            ticket.assigned_team_id = agent.team_id
        agent.current_workload += 1

    if assign_in.team_id is not None:
        team_res = await db.execute(select(Team).where(Team.id == assign_in.team_id))
        team = team_res.scalar_one_or_none()
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        ticket.assigned_team_id = team.id

    history = TicketHistory(
        ticket_id=ticket.id,
        old_status=ticket.status,
        new_status=ticket.status,
        changed_by=current_user.id,
    )
    db.add(history)
    ticket.history.insert(0, history)

    await db.commit()
    return await ticket_service.get_ticket_by_id(db, ticket.id, current_user, check_permission=False)
