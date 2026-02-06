from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class BucketConfig:
    """
    capacity: maximum tokens the bucket can hold.
    refill_rate_per_sec: tokens added per second (can be fractional).
    """
    capacity: float
    refill_rate_per_sec: float

    def __post_init__(self):
        if self.capacity <= 0:
            raise ValueError("capacity must be > 0")
        if self.refill_rate_per_sec <= 0:
            raise ValueError("refill_rate_per_sec must be > 0")


@dataclass(frozen=True)
class BucketState:
    """
    tokens: current tokens in the bucket (float to allow fractions).
    last_refill_ts: epoch seconds when we last refilled (float).
    """
    tokens: float
    last_refill_ts: float

    def __post_init__(self):
        if self.tokens < 0:
            raise ValueError("tokens cannot be negative")


@dataclass(frozen=True)
class Decision:
    """
    allowed: whether the request is allowed.
    remaining_tokens: tokens left after decision (or before if denied).
    retry_after_s: seconds until enough tokens accrue (None if not applicable,
                   e.g., when cost > capacity and can never be satisfied).
    """
    allowed: bool
    remaining_tokens: float
    retry_after_s: Optional[float]


def _refill(config: BucketConfig, state: BucketState, now_s: float) -> BucketState:
    """Pure refill: return a NEW state with tokens advanced to 'now_s'."""
    if now_s <= state.last_refill_ts:
        return state
    elapsed = now_s - state.last_refill_ts
    added = elapsed * config.refill_rate_per_sec
    new_tokens = min(config.capacity, state.tokens + added)
    # round small negative/epsilon
    if new_tokens < 0 and new_tokens > -1e-12:
        new_tokens = 0.0
    return BucketState(tokens=new_tokens, last_refill_ts=now_s)


def try_consume(
    config: BucketConfig,
    state: BucketState,
    cost: float,
    now_s: float,
) -> Tuple[Decision, BucketState]:
    """
    Attempt to consume 'cost' tokens at time 'now_s'.
    - Returns a Decision and the NEW state (pure; does not mutate input).
    - If cost <= 0, always allowed and state unchanged (post-refill).
    - If cost > capacity, deny permanently (retry_after_s=None).
    """
    if not math.isfinite(cost):
        raise ValueError("cost must be finite")
    if cost < 0:
        raise ValueError("cost must be >= 0")

    # Refill first
    s = _refill(config, state, now_s)

    if cost == 0:
        return Decision(True, s.tokens, 0.0), s

    if cost > config.capacity:
        # Impossible request: cannot ever accumulate more than capacity
        return Decision(False, s.tokens, None), s

    if s.tokens + 1e-12 >= cost:
        new_tokens = s.tokens - cost
        new_state = BucketState(tokens=new_tokens, last_refill_ts=s.last_refill_ts)
        return Decision(True, new_tokens, 0.0), new_state

    # Not enough tokens: compute time needed
    needed = cost - s.tokens
    retry_after = needed / config.refill_rate_per_sec
    # Avoid tiny negatives due to floating point
    if retry_after < 0 and retry_after > -1e-12:
        retry_after = 0.0
    return Decision(False, s.tokens, retry_after), s
