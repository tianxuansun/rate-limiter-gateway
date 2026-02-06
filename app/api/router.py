from fastapi import APIRouter

from app.api.routes import checks, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(checks.router, prefix="/check", tags=["RateLimit"])