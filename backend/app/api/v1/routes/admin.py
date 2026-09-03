from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AdminAnalyticsResponse, AgentWorkloadResponse, PaginatedUserList, TicketAssignRequest
from app.schemas.ticket import PaginatedTicketList, TicketResponse
from app.services import admin_service, ticket_service

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_role("admin"))])


@router.get("/tickets", response_model=PaginatedTicketList, status_code=status.HTTP_200_OK, summary="Admin Ticket List")
async def admin_list_tickets(
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    team_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a paginated list of all system tickets for administrator review.
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


@router.get("/users", response_model=PaginatedUserList, status_code=status.HTTP_200_OK, summary="Admin User List")
async def admin_list_users(
    role: Optional[str] = Query(default=None, description="Filter by user role"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a paginated list of registered system users.
    """
    return await admin_service.get_users(db, page=page, page_size=page_size, role_filter=role)


@router.get("/agents", response_model=List[AgentWorkloadResponse], status_code=status.HTTP_200_OK, summary="Admin Agent Workload List")
async def admin_list_agents(
    db: AsyncSession = Depends(get_db),
):
    """
    Lists support agents alongside assigned team name, current workload count, and availability.
    """
    return await admin_service.get_agents_with_workload(db)


@router.get("/analytics", response_model=AdminAnalyticsResponse, status_code=status.HTTP_200_OK, summary="Admin Analytics Dashboard")
async def admin_analytics(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns real-time aggregated metrics: totals, status breakdown, category breakdown, priority breakdown, SLA escalation count, and average resolution time.
    """
    return await admin_service.get_analytics(db)


@router.put("/tickets/{id}/assign", response_model=TicketResponse, status_code=status.HTTP_200_OK, summary="Admin Manual Ticket Assignment")
async def admin_assign_ticket(
    id: str,
    assign_in: TicketAssignRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually assigns a support ticket to a specific agent or support team.
    """
    ticket = await admin_service.assign_ticket(db, id, assign_in, current_user)
    return TicketResponse.model_validate(ticket)
