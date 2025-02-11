from redis import asyncio as aioredis

from Worker.config.config import config


async def get_redis_client():
    _redis_client = await aioredis.from_url(
        config.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    return _redis_client
