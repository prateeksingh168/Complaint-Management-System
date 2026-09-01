from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ticket import PaginatedTicketList, TicketCreate, TicketResponse, TicketStatusUpdate, TicketUpdate
from app.services import ticket_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED, summary="Create Ticket")
async def create_ticket(
    ticket_in: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually creates a support ticket for an existing complaint.
    """
    ticket = await ticket_service.create_ticket(db, ticket_in)
    return TicketResponse.model_validate(ticket)


@router.get("", response_model=PaginatedTicketList, status_code=status.HTTP_200_OK, summary="List Tickets")
async def list_tickets(
    status: Optional[str] = Query(default=None, description="Filter by status"),
    priority: Optional[str] = Query(default=None, description="Filter by priority"),
    team_id: Optional[int] = Query(default=None, description="Filter by assigned team ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a paginated list of support tickets with status, priority, and team filters.
    """
    return await ticket_service.get_tickets(
        db=db,
        current_user=current_user,
        status_filter=status,
        priority_filter=priority,
        team_id_filter=team_id,
        page=page,
        page_size=page_size,
    )


@router.get("/{id}", response_model=TicketResponse, status_code=status.HTTP_200_OK, summary="Get Ticket Details")
async def get_ticket(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves full details of a ticket including assignment info and complete status change history.
    """
    ticket = await ticket_service.get_ticket_by_id(db, id, current_user)
    return TicketResponse.model_validate(ticket)


@router.put("/{id}", response_model=TicketResponse, status_code=status.HTTP_200_OK, summary="Update Ticket")
async def update_ticket(
    id: str,
    update_in: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates general ticket fields (priority, assignment, escalation).
    """
    ticket = await ticket_service.update_ticket(db, id, current_user, update_in)
    return TicketResponse.model_validate(ticket)


@router.put("/{id}/status", response_model=TicketResponse, status_code=status.HTTP_200_OK, summary="Update Ticket Status")
async def update_ticket_status(
    id: str,
    status_in: TicketStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes state machine status transition (Registered -> In Progress -> Under Review -> Resolved),
    writes an audit row to `ticket_history`, and updates resolved timestamps.
    """
    ticket = await ticket_service.update_ticket_status(db, id, current_user, status_in)
    return TicketResponse.model_validate(ticket)
