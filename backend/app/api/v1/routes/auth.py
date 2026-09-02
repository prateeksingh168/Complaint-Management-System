import time
from collections import defaultdict
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import AuthResponse, RefreshRequest, Token, UserLogin, UserRegister, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

# Simple in-memory rate limiter for login
LOGIN_ATTEMPTS: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
MAX_LOGIN_ATTEMPTS = 10  # attempts per window


def check_rate_limit(request: Request):
    """Basic in-memory rate limiter for authentication endpoints."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Clean up old timestamps
    attempts = [t for t in LOGIN_ATTEMPTS[client_ip] if now - t < RATE_LIMIT_WINDOW]
    LOGIN_ATTEMPTS[client_ip] = attempts

    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )
    
    LOGIN_ATTEMPTS[client_ip].append(now)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED, summary="Register User")
async def register(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Registers a new user (default role: 'user') and returns user profile with JWT access & refresh tokens.
    """
    return await auth_service.register_user(db, user_in)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK, summary="User Login")
async def login(
    login_in: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticates user with email and password, returning JWT access & refresh tokens. Rate-limited per client IP.
    """
    check_rate_limit(request)
    return await auth_service.authenticate_user(db, login_in)


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK, summary="Refresh Access Token")
async def refresh_token(
    refresh_in: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchanges a valid refresh token for a new pair of access and refresh tokens.
    """
    return await auth_service.refresh_access_token(db, refresh_in.refresh_token)


@router.get("/profile", response_model=UserResponse, status_code=status.HTTP_200_OK, summary="Get Current User Profile")
async def profile(
    current_user: User = Depends(get_current_user),
):
    """
    Returns the authenticated user profile information. Requires Authorization header with valid Bearer token.
    """
    return UserResponse.model_validate(current_user)
