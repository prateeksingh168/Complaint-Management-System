from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.user import AuthResponse, Token, UserLogin, UserRegister, UserResponse


async def register_user(db: AsyncSession, user_in: UserRegister) -> AuthResponse:
    """Registers a new user and returns user info with JWT tokens."""
    # Check if user email already exists
    stmt = select(User).where(User.email == user_in.email.lower())
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user record
    new_user = User(
        name=user_in.name,
        email=user_in.email.lower(),
        password_hash=get_password_hash(user_in.password),
        role=user_in.role.value if hasattr(user_in.role, 'value') else str(user_in.role),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT tokens
    access_token = create_access_token(subject=new_user.id, role=new_user.role)
    refresh_token = create_refresh_token(subject=new_user.id, role=new_user.role)

    return AuthResponse(
        user=UserResponse.model_validate(new_user),
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        ),
    )


async def authenticate_user(db: AsyncSession, login_in: UserLogin) -> Token:
    """Authenticates user credentials and returns new access/refresh tokens."""
    stmt = select(User).where(User.email == login_in.email.lower())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id, role=user.role)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Token:
    """Validates refresh token and generates new token pair."""
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token type",
        )

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = create_access_token(subject=user.id, role=user.role)
    new_refresh_token = create_refresh_token(subject=user.id, role=user.role)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
