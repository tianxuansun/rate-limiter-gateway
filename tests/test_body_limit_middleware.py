import httpx
import pytest
from fastapi import FastAPI

from app.core.body_limit_middleware import BodyLimitMiddleware


def _make_app(max_body_bytes: int) -> FastAPI:
    app = FastAPI()
    app.add_middleware(BodyLimitMiddleware, max_body_bytes=max_body_bytes, path_prefix="/api")

    @app.post("/api/echo")
    async def echo(payload: dict):
        return payload

    return app


@pytest.mark.asyncio
async def test_allows_small_body():
    app = _make_app(max_body_bytes=1024)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/api/echo", json={"x": "ok"})
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_rejects_large_body():
    app = _make_app(max_body_bytes=64)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/api/echo", json={"x": "a" * 500})
        assert r.status_code == 413
