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
    """Returns SLA escalation threshold in hours based on priority level."""
    mapping = {
        "Urgent": settings.ESCALATION_HOURS_URGENT,
        "High": settings.ESCALATION_HOURS_HIGH,
        "Medium": settings.ESCALATION_HOURS_MEDIUM,
        "Low": settings.ESCALATION_HOURS_LOW,
    }
    return mapping.get(priority, settings.ESCALATION_HOURS_MEDIUM)


async def check_and_escalate_tickets(db: AsyncSession) -> List[Ticket]:
    """
    Scans unresolved tickets for SLA threshold breaches.
    Updates breached tickets with escalated=True, escalated_at=now(), records history entries, and creates user notifications.
    """
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.complaint), selectinload(Ticket.history))
        .where(Ticket.status != "Resolved", Ticket.escalated == False)
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
            ticket.escalated = True
            ticket.escalated_at = now

            system_actor_id = ticket.complaint.user_id if ticket.complaint else ticket.id

            history = TicketHistory(
                ticket_id=ticket.id,
                old_status=ticket.status,
                new_status=ticket.status,
                changed_by=system_actor_id,
                note=f"Ticket escalated due to SLA breach ({ticket.priority} threshold of {threshold_hours}h exceeded).",
            )
            db.add(history)
            ticket.history.insert(0, history)

            if ticket.complaint:
                notif = Notification(
                    user_id=ticket.complaint.user_id,
                    ticket_id=ticket.id,
                    message=f"Ticket {ticket.ticket_id} has been escalated due to SLA resolution threshold breach.",
                )
                db.add(notif)

            escalated_tickets.append(ticket)

    if escalated_tickets:
        await db.commit()

    return escalated_tickets
