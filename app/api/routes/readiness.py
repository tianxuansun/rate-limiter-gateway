from fastapi import APIRouter, Depends

from app.api.deps import get_redis

router = APIRouter()


@router.get("", summary="Readiness (checks Redis)")
async def readyz(r=Depends(get_redis)):
    # If Redis is down, this will raise and return 500 by default
    pong = await r.ping()
    return {"ready": True, "redis": pong}
