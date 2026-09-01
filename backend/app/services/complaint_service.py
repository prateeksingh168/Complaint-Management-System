import random
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.complaint import Complaint
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintResponse, ComplaintUpdate, PaginatedComplaintList
from app.services import ai_client


async def generate_complaint_id(db: AsyncSession) -> str:
    """Generates unique human-readable complaint identifier CMP-XXXXX."""
    stmt = select(func.count(Complaint.id))
    result = await db.execute(stmt)
    count = result.scalar() or 0
    next_num = 10000 + count + 1
    return f"CMP-{next_num}"


async def validate_or_get_category(db: AsyncSession, category_name: str, requested_category_id: Optional[int] = None) -> Category:
    """
    Validates category against live DB table (PRD Section 6 rule #4).
    If requested_category_id is provided, validates that category ID.
    Otherwise searches by category_name; if missing/inactive, falls back to 'Other'.
    """
    if requested_category_id is not None:
        stmt = select(Category).where(Category.id == requested_category_id, Category.is_active == True)
        res = await db.execute(stmt)
        cat = res.scalar_one_or_none()
        if cat:
            return cat

    # Search by category name
    stmt = select(Category).where(func.lower(Category.name) == category_name.lower(), Category.is_active == True)
    res = await db.execute(stmt)
    cat = res.scalar_one_or_none()

    if cat:
        return cat

    # Fallback to 'Other' category row from DB
    stmt_other = select(Category).where(func.lower(Category.name) == "other", Category.is_active == True)
    res_other = await db.execute(stmt_other)
    other_cat = res_other.scalar_one_or_none()

    if not other_cat:
        # If 'Other' row doesn't exist yet, create it dynamically
        other_cat = Category(name="Other", is_active=True)
        db.add(other_cat)
        await db.commit()
        await db.refresh(other_cat)

    return other_cat


async def create_complaint(
    db: AsyncSession,
    user_id: str,
    complaint_in: ComplaintCreate,
) -> Complaint:
    """
    Creates a new complaint, performs AI/fallback classification,
    validates category in DB, and generates a linked ticket.
    """
    # Run AI or fallback classification
    ai_result = await ai_client.classify_complaint(complaint_in.text)

    category_name = ai_result.get("category", "Other")
    priority = complaint_in.priority or ai_result.get("priority", "Medium")
    ai_confidence = ai_result.get("confidence")
    complexity = complaint_in.complexity or "Medium"

    # Validate category against live DB table
    cat = await validate_or_get_category(db, category_name, complaint_in.category_id)

    # Generate human ID
    cmp_id = await generate_complaint_id(db)

    # Save Complaint
    complaint = Complaint(
        complaint_id=cmp_id,
        user_id=user_id,
        text=complaint_in.text,
        category_id=cat.id,
        priority=priority,
        complexity=complexity,
        status="Registered",
    )
    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)

    # Create linked ticket automatically
    ticket = Ticket(
        ticket_id=cmp_id,
        complaint_id=complaint.id,
        status="Registered",
        priority=priority,
        ai_confidence=ai_confidence,
    )
    db.add(ticket)
    await db.commit()

    # Re-fetch complaint with category relationship loaded
    stmt = select(Complaint).options(selectinload(Complaint.category), selectinload(Complaint.ticket)).where(Complaint.id == complaint.id)
    res = await db.execute(stmt)
    return res.scalar_one()


async def get_complaints(
    db: AsyncSession,
    current_user: User,
    status_filter: Optional[str] = None,
    category_id_filter: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedComplaintList:
    """Fetches paginated complaints list with filtering and ownership enforcement."""
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    stmt = select(Complaint).options(selectinload(Complaint.category), selectinload(Complaint.ticket))

    # Ownership check: non-admin/agent users only see their own complaints
    if current_user.role == "user":
        stmt = stmt.where(Complaint.user_id == current_user.id)

    if status_filter:
        stmt = stmt.where(Complaint.status == status_filter)

    if category_id_filter:
        stmt = stmt.where(Complaint.category_id == category_id_filter)

    # Count query
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    # Paginated items query
    stmt = stmt.order_by(Complaint.created_at.desc()).offset(offset).limit(page_size)
    items_res = await db.execute(stmt)
    complaints = items_res.scalars().all()

    response_items = []
    for c in complaints:
        item = ComplaintResponse.model_validate(c)
        if c.ticket:
            item.ticket_id = c.ticket.id
        response_items.append(item)

    return PaginatedComplaintList(
        total=total,
        page=page,
        page_size=page_size,
        items=response_items,
    )


async def get_complaint_by_id(
    db: AsyncSession,
    complaint_id_or_human_id: str,
    current_user: User,
) -> Complaint:
    """Fetches complaint details by UUID or human CMP-XXXXX ID."""
    stmt = (
        select(Complaint)
        .options(selectinload(Complaint.category), selectinload(Complaint.ticket))
        .where((Complaint.id == complaint_id_or_human_id) | (Complaint.complaint_id == complaint_id_or_human_id))
    )
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    # Permission check: user can only view their own complaint, admin/agent can view all
    if current_user.role == "user" and complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this complaint",
        )

    return complaint


async def update_complaint(
    db: AsyncSession,
    complaint_id: str,
    current_user: User,
    update_in: ComplaintUpdate,
) -> Complaint:
    """Updates an existing complaint."""
    complaint = await get_complaint_by_id(db, complaint_id, current_user)

    if update_in.text is not None:
        complaint.text = update_in.text
    if update_in.category_id is not None:
        cat = await validate_or_get_category(db, "", update_in.category_id)
        complaint.category_id = cat.id
    if update_in.priority is not None:
        complaint.priority = update_in.priority
    if update_in.complexity is not None:
        complaint.complexity = update_in.complexity
    if update_in.status is not None:
        complaint.status = update_in.status

    await db.commit()
    return await get_complaint_by_id(db, complaint.id, current_user)
