from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agent import Agent
from app.models.complaint import Complaint
from app.models.notification import Notification
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.models.user import User
from app.schemas.ticket import PaginatedTicketList, TicketCreate, TicketResponse, TicketStatusUpdate, TicketUpdate

# State Machine Transition Table
ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "Registered": {"In Progress", "Resolved"},
    "In Progress": {"Under Review", "Resolved"},
    "Under Review": {"In Progress", "Resolved"},
    "Resolved": set(),  # Terminal state
}


def validate_status_transition(current_status: str, new_status: str) -> None:
    """Validates ticket status state machine rules."""
    if current_status == new_status:
        return

    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status}' to '{new_status}'. Allowed transitions: {list(allowed)}",
        )


async def create_ticket(db: AsyncSession, ticket_in: TicketCreate) -> Ticket:
    """Creates a new ticket manually (or via complaint flow)."""
    stmt = select(Complaint).where((Complaint.id == ticket_in.complaint_id) | (Complaint.complaint_id == ticket_in.complaint_id))
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked complaint not found",
        )

    existing_stmt = select(Ticket).where(Ticket.complaint_id == complaint.id)
    existing_res = await db.execute(existing_stmt)
    existing_ticket = existing_res.scalar_one_or_none()

    if existing_ticket:
        return existing_ticket

    ticket = Ticket(
        ticket_id=complaint.complaint_id,
        complaint_id=complaint.id,
        assigned_team_id=ticket_in.assigned_team_id,
        assigned_agent_id=ticket_in.assigned_agent_id,
        priority=ticket_in.priority or complaint.priority,
        status=ticket_in.status or "Registered",
    )
    db.add(ticket)
    await db.commit()
    return await get_ticket_by_id(db, ticket.id, None, check_permission=False)


async def get_tickets(
    db: AsyncSession,
    current_user: User,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    team_id_filter: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedTicketList:
    """Fetches paginated tickets list with filtering and role permission checks."""
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    stmt = select(Ticket).options(
        selectinload(Ticket.assigned_team),
        selectinload(Ticket.assigned_agent),
        selectinload(Ticket.history),
    )

    if current_user.role == "user":
        stmt = stmt.join(Complaint, Ticket.complaint_id == Complaint.id).where(Complaint.user_id == current_user.id)
    elif current_user.role == "agent":
        agent_stmt = select(Agent).where(Agent.user_id == current_user.id)
        agent_res = await db.execute(agent_stmt)
        agent_profile = agent_res.scalar_one_or_none()

        if agent_profile:
            stmt = stmt.where(
                (Ticket.assigned_agent_id == agent_profile.id)
                | (Ticket.assigned_team_id == agent_profile.team_id)
                | (Ticket.assigned_team_id.is_(None))
            )

    if status_filter:
        stmt = stmt.where(Ticket.status == status_filter)
    if priority_filter:
        stmt = stmt.where(Ticket.priority == priority_filter)
    if team_id_filter:
        stmt = stmt.where(Ticket.assigned_team_id == team_id_filter)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    stmt = stmt.order_by(Ticket.created_at.desc()).offset(offset).limit(page_size)
    items_res = await db.execute(stmt)
    tickets = items_res.scalars().all()

    items = [TicketResponse.model_validate(t) for t in tickets]

    return PaginatedTicketList(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


async def get_ticket_by_id(
    db: AsyncSession,
    ticket_id_or_human_id: str,
    current_user: Optional[User] = None,
    check_permission: bool = True,
) -> Ticket:
    """Retrieves ticket details along with change history and assignments."""
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.assigned_team),
            selectinload(Ticket.assigned_agent),
            selectinload(Ticket.history),
            selectinload(Ticket.complaint),
        )
        .where((Ticket.id == ticket_id_or_human_id) | (Ticket.ticket_id == ticket_id_or_human_id))
    )
    res = await db.execute(stmt)
    ticket = res.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    if check_permission and current_user and current_user.role == "user":
        if ticket.complaint.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this ticket",
            )

    return ticket


async def update_ticket(
    db: AsyncSession,
    ticket_id: str,
    current_user: User,
    update_in: TicketUpdate,
) -> Ticket:
    """Updates general ticket attributes."""
    ticket = await get_ticket_by_id(db, ticket_id, current_user)
    target_id = ticket.id

    if update_in.assigned_team_id is not None:
        ticket.assigned_team_id = update_in.assigned_team_id
    if update_in.assigned_agent_id is not None:
        ticket.assigned_agent_id = update_in.assigned_agent_id
    if update_in.priority is not None:
        ticket.priority = update_in.priority
    if update_in.escalated is not None:
        ticket.escalated = update_in.escalated
        if update_in.escalated and not ticket.escalated_at:
            ticket.escalated_at = datetime.now(timezone.utc)

    if update_in.status is not None and update_in.status != ticket.status:
        validate_status_transition(ticket.status, update_in.status)
        old_status = ticket.status
        ticket.status = update_in.status

        if update_in.status == "Resolved":
            ticket.resolved_at = datetime.now(timezone.utc)

        history = TicketHistory(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=update_in.status,
            changed_by=current_user.id,
            note="Status updated via general ticket update",
        )
        db.add(history)
        ticket.history.insert(0, history)

        if ticket.complaint:
            notif = Notification(
                user_id=ticket.complaint.user_id,
                ticket_id=ticket.id,
                message=f"Your ticket {ticket.ticket_id} status has been updated to {update_in.status}.",
            )
            db.add(notif)

    await db.commit()
    return await get_ticket_by_id(db, target_id, current_user)


async def update_ticket_status(
    db: AsyncSession,
    ticket_id: str,
    current_user: User,
    status_in: TicketStatusUpdate,
) -> Ticket:
    """Updates ticket status via state machine, logs entry in ticket_history, and creates a user notification."""
    ticket = await get_ticket_by_id(db, ticket_id, current_user)
    target_id = ticket.id
    old_status = ticket.status
    new_status = status_in.status

    validate_status_transition(old_status, new_status)

    ticket.status = new_status
    if new_status == "Resolved":
        ticket.resolved_at = datetime.now(timezone.utc)

    if ticket.complaint:
        ticket.complaint.status = new_status

        # Trigger notification
        notif = Notification(
            user_id=ticket.complaint.user_id,
            ticket_id=ticket.id,
            message=f"Your ticket {ticket.ticket_id} status has been updated to '{new_status}'.",
        )
        db.add(notif)

    history = TicketHistory(
        ticket_id=ticket.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
        note=status_in.note,
    )
    db.add(history)
    ticket.history.insert(0, history)

    await db.commit()
    return await get_ticket_by_id(db, target_id, current_user)
