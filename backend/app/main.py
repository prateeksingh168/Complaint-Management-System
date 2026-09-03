from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.exceptions import (
    ComplaintSystemException,
    complaint_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} (v{settings.VERSION}) in [{settings.ENVIRONMENT}] mode")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Exception Handlers for Consistent Error Envelopes
app.add_exception_handler(ComplaintSystemException, complaint_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }


@app.get("/health", include_in_schema=False)
async def root_health():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
