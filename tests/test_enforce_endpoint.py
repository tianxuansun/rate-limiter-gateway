import httpx
import pytest
from asgi_lifespan import LifespanManager

from app.main import create_app


@pytest.mark.asyncio
async def test_enforce_returns_429_when_denied():
    app = create_app()

    # This runs FastAPI lifespan startup/shutdown so app.state.redis is set
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            r1 = await c.post("/api/enforce", json={"key": "t1", "cost": 5})
            assert r1.status_code == 200

            r2 = await c.post("/api/enforce", json={"key": "t1", "cost": 1})
            assert r2.status_code == 429

            headers = {k.lower() for k in r2.headers.keys()}
            assert "ratelimit-limit" in headers
            assert "ratelimit-remaining" in headers
            assert "ratelimit-reset" in headers
            assert "retry-after" in headers
