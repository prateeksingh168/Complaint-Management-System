from datetime import datetime, timezone
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.notification import Notification
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory


def get_escalation_threshold_hours(priority: str) -> int:
    mapping = {
        "Urgent": settings.ESCALATION_HOURS_URGENT,
        "High": settings.ESCALATION_HOURS_HIGH,
        "Medium": settings.ESCALATION_HOURS_MEDIUM,
        "Low": settings.ESCALATION_HOURS_LOW,
    }
    return mapping.get(priority, settings.ESCALATION_HOURS_MEDIUM)


async def check_and_escalate_tickets(db: AsyncSession) -> List[Ticket]:
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.complaint), selectinload(Ticket.history))
        .where(Ticket.status != "Resolved")
    )
    res = await db.execute(stmt)
    unresolved_tickets: List[Ticket] = res.scalars().all()

    now = datetime.now(timezone.utc)
    escalated_tickets: List[Ticket] = []

    for ticket in unresolved_tickets:
        threshold_hours = get_escalation_threshold_hours(ticket.priority)
        
        created_at = ticket.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age_hours = (now - created_at).total_seconds() / 3600.0

        if age_hours >= threshold_hours:
            system_user_id = ticket.complaint.user_id if ticket.complaint else None

            history = TicketHistory(
                ticket_id=ticket.id,
                old_status=ticket.status,
                new_status=ticket.status,
                changed_by=system_user_id,
            )
            db.add(history)
            ticket.history.insert(0, history)

            if ticket.complaint and ticket.complaint.user_id:
                notif = Notification(
                    user_id=ticket.complaint.user_id,
                    ticket_id=ticket.id,
                    message=f"Ticket {ticket.ticket_number} has been escalated due to SLA resolution threshold breach.",
                    type="escalation",
                )
                db.add(notif)

            escalated_tickets.append(ticket)

    if escalated_tickets:
        await db.commit()

    return escalated_tickets
