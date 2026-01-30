from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.deps import get_redis
from app.core.config import settings
from app.ratelimit.redis_bucket import try_consume_redis, Decision

router = APIRouter()

class CheckRequest(BaseModel):
    key: str = Field(min_length=1)
    cost: float = Field(ge=0)
    # Optional per-call overrides (else use defaults from settings)
    capacity: float | None = Field(default=None, gt=0)
    refill_rate_per_sec: float | None = Field(default=None, gt=0)

class CheckResponse(BaseModel):
    allowed: bool
    remaining_tokens: float
    retry_after_s: float | None

@router.post("", response_model=CheckResponse, summary="Rate-limit decision (token bucket)")
async def check_rate_limit(req: CheckRequest, r = Depends(get_redis)):
    cap = req.capacity if req.capacity is not None else settings.BUCKET_CAPACITY
    rate = (
        req.refill_rate_per_sec
        if req.refill_rate_per_sec is not None
        else settings.BUCKET_REFILL_RATE_PER_SEC
    )

    # guard against silly inputs
    if req.cost > cap:
        # Still run Redis to update refill state; but we know it's deny
        decision: Decision = await try_consume_redis(
            r,
            req.key,
            capacity=cap,
            refill_rate_per_sec=rate,
            cost=req.cost,
            prefix=settings.REDIS_KEY_PREFIX,
        )
        return CheckResponse(
            allowed=False,
            remaining_tokens=decision.remaining_tokens,
            retry_after_s=None,
        )

    decision: Decision = await try_consume_redis(
        r,
        req.key,
        capacity=cap,
        refill_rate_per_sec=rate,
        cost=req.cost,
        prefix=settings.REDIS_KEY_PREFIX,
    )
    return CheckResponse(
        allowed=decision.allowed,
        remaining_tokens=decision.remaining_tokens,
        retry_after_s=decision.retry_after_s,
    )
