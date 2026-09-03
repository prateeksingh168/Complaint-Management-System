from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
async def health_check():
    """
    Health check endpoint returning application status and environment information.
    """
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
