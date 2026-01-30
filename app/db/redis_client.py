import redis.asyncio as redis
from app.core.config import settings

def create_redis():
    # decode_responses=True gives you str; numbers from Lua come back as float/int cleanly
    return redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
