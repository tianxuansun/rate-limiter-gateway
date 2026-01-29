from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

class CheckRequest(BaseModel):
    key: str = Field(min_length=1)
    cost: float = Field(ge=0)

class CheckResponse(BaseModel):
    allowed: bool
    remaining_tokens: float | None = None
    retry_after_s: float | None = None

@router.post("", response_model=CheckResponse, summary="(Stub) rate-limit decision")
async def check_rate_limit(req: CheckRequest):
    # Day 3: will call Redis-backed token bucket.
    # For now, return a stub to keep the contract visible.
    return CheckResponse(allowed=True, remaining_tokens=None, retry_after_s=0.0)
