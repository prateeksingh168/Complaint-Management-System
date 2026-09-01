from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintResponse, ComplaintUpdate, PaginatedComplaintList
from app.services import complaint_service

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED, summary="Create Complaint")
async def create_complaint(
    complaint_in: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submits a new complaint text. Automatically triggers AI (or fallback) category & priority classification,
    validates category against live DB tables, and creates a linked ticket.
    """
    complaint = await complaint_service.create_complaint(db, current_user.id, complaint_in)
    res = ComplaintResponse.model_validate(complaint)
    if complaint.ticket:
        res.ticket_id = complaint.ticket.id
    return res


@router.get("", response_model=PaginatedComplaintList, status_code=status.HTTP_200_OK, summary="List Complaints")
async def list_complaints(
    status: Optional[str] = Query(default=None, description="Filter by complaint status"),
    category_id: Optional[int] = Query(default=None, description="Filter by category ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a paginated list of complaints. Users see their own complaints; Admins/Agents see all complaints.
    """
    return await complaint_service.get_complaints(
        db=db,
        current_user=current_user,
        status_filter=status,
        category_id_filter=category_id,
        page=page,
        page_size=page_size,
    )


@router.get("/{id}", response_model=ComplaintResponse, status_code=status.HTTP_200_OK, summary="Get Complaint Details")
async def get_complaint(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves complaint details by complaint UUID or human CMP-XXXXX ID along with linked ticket info.
    """
    complaint = await complaint_service.get_complaint_by_id(db, id, current_user)
    res = ComplaintResponse.model_validate(complaint)
    if complaint.ticket:
        res.ticket_id = complaint.ticket.id
    return res


@router.put("/{id}", response_model=ComplaintResponse, status_code=status.HTTP_200_OK, summary="Update Complaint")
async def update_complaint(
    id: str,
    update_in: ComplaintUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates an existing complaint's details (text, status, category, or priority). Owner or Admin only.
    """
    complaint = await complaint_service.update_complaint(db, id, current_user, update_in)
    res = ComplaintResponse.model_validate(complaint)
    if complaint.ticket:
        res.ticket_id = complaint.ticket.id
    return res
