from fastapi import APIRouter

from app.domain.admin.router import admin_router

api_router = APIRouter()

api_router.include_router(admin_router)