from __future__ import annotations
from typing import Optional, Tuple
import time

import redis.asyncio as redis

# Atomic token-bucket in Lua:
# KEYS[1] = bucket key
# ARGV: capacity, rate_per_sec, cost, now_s
# Returns: {allowed(0/1), remaining_tokens(float), retry_after(float or -1)}
LUA_TOKEN_BUCKET = r"""
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local cost = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

local tokens = tonumber(redis.call('HGET', key, 'tokens'))
local last = tonumber(redis.call('HGET', key, 'last'))

if tokens == nil or last == nil then
  tokens = capacity
  last = now
end

if now > last then
  local elapsed = now - last
  tokens = math.min(capacity, tokens + elapsed * rate)
end

if cost > capacity then
  -- impossible request, still write back refilled state
  redis.call('HSET', key, 'tokens', tokens, 'last', now)
  return {0, tokens, -1}
end

if tokens + 1e-12 >= cost then
  tokens = tokens - cost
  redis.call('HSET', key, 'tokens', tokens, 'last', now)
  return {1, tokens, 0}
else
  local needed = cost - tokens
  local retry_after = needed / rate
  redis.call('HSET', key, 'tokens', tokens, 'last', now)
  return {0, tokens, retry_after}
end
"""

class Decision:
    def __init__(self, allowed: bool, remaining_tokens: float, retry_after_s: Optional[float]):
        self.allowed = allowed
        self.remaining_tokens = remaining_tokens
        self.retry_after_s = retry_after_s

async def try_consume_redis(
    r: "redis.Redis",
    key: str,
    *,
    capacity: float,
    refill_rate_per_sec: float,
    cost: float,
    now_s: Optional[float] = None,
    prefix: str = "bucket:",
) -> Decision:
    if now_s is None:
        now_s = time.time()
    redis_key = f"{prefix}{key}"

    # eval <script> numkeys key argv...
    res = await r.eval(
        LUA_TOKEN_BUCKET,
        1,
        redis_key,
        str(capacity),
        str(refill_rate_per_sec),
        str(cost),
        str(now_s),
    )
    # res is [allowed_int, remaining, retry_after]
    allowed_int, remaining, retry_after = res
    if isinstance(allowed_int, str):
        allowed_int = int(allowed_int)
    if isinstance(remaining, str):
        remaining = float(remaining)
    if isinstance(retry_after, str):
        retry_after = float(retry_after)

    if retry_after == -1:
        retry_after = None

    return Decision(bool(allowed_int), float(remaining), retry_after)
