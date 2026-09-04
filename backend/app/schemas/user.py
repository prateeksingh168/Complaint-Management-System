from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Jane Doe"})
    email: EmailStr = Field(..., json_schema_extra={"example": "jane.doe@example.com"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "SecurePassword123!"})
    role: str = Field(default="user", json_schema_extra={"example": "user"})


UserCreate = UserRegister


class UserLogin(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "jane.doe@example.com"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "SecurePassword123!"})


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., json_schema_extra={"example": "refresh_token_string"})


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


Token = TokenResponse


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
