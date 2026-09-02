import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    PROJECT_NAME: str = "Complaint Management System Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security & Auth
    JWT_SECRET: str = Field(default="dev-secret-key-complaint-management-system-2026")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres_password")
    POSTGRES_DB: str = Field(default="complaint_db")
    DATABASE_URL: Optional[str] = Field(default=None)

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            # Ensure asyncpg driver is used for SQLAlchemy async engine
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # AI Module Integration
    AI_SERVICE_URL: str = Field(default="http://localhost:8001")
    AI_REQUEST_TIMEOUT_SECONDS: float = Field(default=3.0)

    # Assignment Weights (Rule-based scoring)
    SKILL_MATCH_WEIGHT: float = Field(default=0.3)
    AVAILABILITY_WEIGHT: float = Field(default=0.25)
    WORKLOAD_WEIGHT: float = Field(default=0.25)
    CATEGORY_MATCH_WEIGHT: float = Field(default=0.1)
    PRIORITY_WEIGHT: float = Field(default=0.1)

    # Escalation Hours per priority level
    ESCALATION_HOURS_URGENT: int = Field(default=2)
    ESCALATION_HOURS_HIGH: int = Field(default=8)
    ESCALATION_HOURS_MEDIUM: int = Field(default=24)
    ESCALATION_HOURS_LOW: int = Field(default=72)


settings = Settings()
