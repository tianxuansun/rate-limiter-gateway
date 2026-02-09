from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import RequestIdMiddleware, setup_logging
from app.core.metrics_middleware import MetricsMiddleware
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

    # Middlewares
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(MetricsMiddleware)

    # Health for infra probes
    @app.get("/healthz", tags=["Health"])
    async def healthz():
        return {"ok": True}

    # Prometheus scrape endpoint
    @app.get("/metrics", tags=["Observability"])
    async def metrics():
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    # Versioned API
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
