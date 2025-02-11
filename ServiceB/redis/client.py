from redis import asyncio as aioredis

from ServiceB.config.config import config


async def get_redis_client():
    return await aioredis.from_url(config.REDIS_URL, decode_responses=True)
