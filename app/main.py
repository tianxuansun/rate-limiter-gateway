from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging, RequestIdMiddleware
from app.db.redis_client import create_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.redis = create_redis()
    try:
        yield
    finally:
        # shutdown
        await app.state.redis.aclose()

def create_app() -> FastAPI:
    setup_logging(settings.LOG_LEVEL)
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.add_middleware(RequestIdMiddleware)

    @app.get("/healthz", tags=["Health"])
    async def healthz():
        return {"ok": True}

    app.include_router(api_router, prefix="/api")
    return app

app = create_app()
