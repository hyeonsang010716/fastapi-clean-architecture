from fastapi import APIRouter

from app.api.v1.user import register, sse

router = APIRouter(prefix="/user")

router.include_router(register.router)
router.include_router(sse.router)