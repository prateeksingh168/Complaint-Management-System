from fastapi import APIRouter
from app.api.v1.routes import admin, auth, chat, complaints, health, notifications, tickets

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(complaints.router)
api_router.include_router(tickets.router)
api_router.include_router(chat.router)
api_router.include_router(admin.router)
api_router.include_router(notifications.router)
