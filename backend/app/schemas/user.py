from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    ADMIN = "admin"


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "John Doe"})
    email: EmailStr = Field(..., json_schema_extra={"example": "john.doe@example.com"})
    password: str = Field(..., min_length=6, max_length=128, json_schema_extra={"example": "Secret123!"})
    role: Optional[UserRole] = Field(default=UserRole.USER)


class UserLogin(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "john.doe@example.com"})
    password: str = Field(..., json_schema_extra={"example": "Secret123!"})


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: Token


class RefreshRequest(BaseModel):
    refresh_token: str
