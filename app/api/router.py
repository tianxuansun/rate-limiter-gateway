from fastapi import APIRouter

from app.api.routes import checks, enforce, health, readiness, version

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(readiness.router, prefix="/readyz", tags=["Health"])
api_router.include_router(checks.router, prefix="/check", tags=["RateLimit"])
api_router.include_router(version.router, prefix="/version", tags=["Meta"])
api_router.include_router(enforce.router, prefix="/enforce", tags=["RateLimit"])
