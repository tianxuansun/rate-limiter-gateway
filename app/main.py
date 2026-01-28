from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging, RequestIdMiddleware

def create_app() -> FastAPI:
    setup_logging(settings.LOG_LEVEL)
    app = FastAPI(title=settings.APP_NAME)
    app.add_middleware(RequestIdMiddleware)

    # Root health (infra probes)
    @app.get("/healthz", tags=["Health"])
    async def healthz():
        return {"ok": True}

    # Versioned API
    app.include_router(api_router, prefix="/api")
    return app

app = create_app()
