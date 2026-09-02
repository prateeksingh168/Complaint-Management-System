from datetime import datetime, timezone
import random
from typing import Optional, Union
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.complaint import Complaint
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, PaginatedComplaintList
from app.services import ai_client, assignment_service


async def generate_complaint_id(db: AsyncSession) -> str:
    """Generates sequential human-readable complaint ID in CMP-XXXXX format."""
    count_stmt = select(func.count(Complaint.complaint_id))
    result = await db.execute(count_stmt)
    total = result.scalar() or 0

    candidate_num = 10001 + total
    while True:
        candidate_id = f"CMP-{candidate_num}"
        exists_stmt = select(Complaint.complaint_id).where(Complaint.complaint_id == candidate_id)
        exists_res = await db.execute(exists_stmt)
        if not exists_res.scalar_one_or_none():
            return candidate_id
        candidate_num += 1


VALID_CATEGORIES = {"Billing", "Technical", "Service", "Account", "Delivery", "Other"}
VALID_PRIORITIES = {"Urgent", "High", "Medium", "Low"}
VALID_COMPLEXITIES = {"Low", "Medium", "High"}
VALID_TEAMS = {
    "General Support",
    "Technical Support",
    "Delivery Support",
    "Billing Support",
    "Service Support",
    "Account Support",
}


async def create_complaint(
    db: AsyncSession,
    user_id: Optional[int],
    complaint_in: ComplaintCreate,
) -> Complaint:
    """Creates complaint, classifies via AI if fields are absent, and auto-spawns linked ticket."""
    ai_classification = await ai_client.classify_complaint(complaint_in.text)

    category = complaint_in.category or ai_classification.get("category", "Other")
    if category not in VALID_CATEGORIES:
        category = "Other"

    priority = complaint_in.priority or ai_classification.get("priority", "Medium")
    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    complexity = complaint_in.complexity or "Medium"
    if complexity not in VALID_COMPLEXITIES:
        complexity = "Medium"

    recommended_team = complaint_in.recommended_team or f"{category} Support" if f"{category} Support" in VALID_TEAMS else "General Support"

    cmp_id = await generate_complaint_id(db)

    complaint = Complaint(
        complaint_id=cmp_id,
        complaint_text=complaint_in.text,
        category=category,
        priority=priority,
        complexity=complexity,
        recommended_team=recommended_team,
        user_id=user_id,
    )
    db.add(complaint)
    await db.flush()

    ticket_number = f"TKT-{cmp_id.split('-')[1]}"
    ticket = Ticket(
        ticket_number=ticket_number,
        complaint_id=complaint.complaint_id,
        category=category,
        priority=priority,
        status="Registered",
    )
    db.add(ticket)
    await db.flush()

    await assignment_service.assign_agent_or_team(db, ticket)

    await db.commit()
    return await get_complaint_by_id(db, cmp_id, user_id=user_id, check_permission=False)


async def get_complaints(
    db: AsyncSession,
    current_user: User,
    category_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    category_id_filter: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedComplaintList:
    """Fetches paginated list of complaints."""
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    stmt = select(Complaint).options(selectinload(Complaint.ticket))

    if current_user.role == "user":
        stmt = stmt.where(Complaint.user_id == current_user.id)

    if category_filter:
        stmt = stmt.where(Complaint.category == category_filter)
    if priority_filter:
        stmt = stmt.where(Complaint.priority == priority_filter)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    stmt = stmt.order_by(Complaint.created_at.desc()).offset(offset).limit(page_size)
    items_res = await db.execute(stmt)
    complaints = items_res.scalars().all()

    items = []
    for c in complaints:
        t_id = c.ticket.ticket_number if c.ticket else None
        items.append(
            {
                "complaint_id": c.complaint_id,
                "complaint_text": c.complaint_text,
                "category": c.category,
                "priority": c.priority,
                "complexity": c.complexity,
                "recommended_team": c.recommended_team,
                "user_id": c.user_id,
                "ticket_id": t_id,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
        )

    return PaginatedComplaintList(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


async def get_complaint_by_id(
    db: AsyncSession,
    complaint_id: str,
    user_id: Optional[int] = None,
    check_permission: bool = True,
) -> Complaint:
    """Retrieves complaint by complaint_id."""
    stmt = (
        select(Complaint)
        .options(selectinload(Complaint.ticket))
        .where(Complaint.complaint_id == complaint_id)
    )
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    if check_permission and user_id is not None:
        if complaint.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this complaint",
            )

    return complaint
