import math

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field

from app.api.deps import get_redis
from app.core.config import settings
from app.metrics import (
    RATE_LIMIT_CHECKS_TOTAL,
    RATE_LIMIT_DECISION_LATENCY_SECONDS,
    RATE_LIMIT_REDIS_ERRORS_TOTAL,
    monotonic_s,
)
from app.ratelimit.redis_bucket import Decision, try_consume_redis

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
async def check_rate_limit(req: CheckRequest, response: Response, r=Depends(get_redis)):
    cap = req.capacity if req.capacity is not None else settings.BUCKET_CAPACITY
    rate = (
        req.refill_rate_per_sec
        if req.refill_rate_per_sec is not None
        else settings.BUCKET_REFILL_RATE_PER_SEC
    )

    # Run the Redis atomic decision (and measure it)
    start = monotonic_s()
    try:
        decision: Decision = await try_consume_redis(
            r,
            req.key,
            capacity=cap,
            refill_rate_per_sec=rate,
            cost=req.cost,
            ttl_sec=settings.BUCKET_KEY_TTL_SEC,
            prefix=settings.REDIS_KEY_PREFIX,
        )
    except Exception:
        RATE_LIMIT_REDIS_ERRORS_TOTAL.inc()
        raise
    finally:
        RATE_LIMIT_DECISION_LATENCY_SECONDS.observe(monotonic_s() - start)

    # Classify result
    if req.cost > cap:
        result = "impossible"
    elif decision.allowed:
        result = "allowed"
    else:
        result = "denied"

    # Metrics
    RATE_LIMIT_CHECKS_TOTAL.labels(result=result).inc()

    # Decision headers (helpful for clients)
    response.headers["X-RateLimit-Decision"] = result
    if result == "impossible":
        response.headers["RateLimit-Reason"] = "cost_exceeds_capacity"
    elif result == "denied":
        response.headers["RateLimit-Reason"] = "insufficient_tokens"

    # Standard-ish rate limit headers
    response.headers["RateLimit-Limit"] = str(cap)
    remaining = max(0, int(math.floor(decision.remaining_tokens)))
    response.headers["RateLimit-Remaining"] = str(remaining)

    reset_s = 0
    if (not decision.allowed) and decision.retry_after_s is not None:
        reset_s = int(math.ceil(decision.retry_after_s))
    response.headers["RateLimit-Reset"] = str(reset_s)

    if not decision.allowed and decision.retry_after_s is not None:
        response.headers["Retry-After"] = str(reset_s)

    # Response body
    if result == "impossible":
        return CheckResponse(
            allowed=False,
            remaining_tokens=decision.remaining_tokens,
            retry_after_s=None,
        )

    return CheckResponse(
        allowed=decision.allowed,
        remaining_tokens=decision.remaining_tokens,
        retry_after_s=decision.retry_after_s,
    )
