import json
from typing import Any, Annotated

from fastapi import Depends
from redis.asyncio import Redis

from backend.core.config import settings


class CacheService:
    def __init__(self, client: Redis):
        self.client = client

    async def get(
            self,
            key: str
    ):
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
            self,
            key: str,
            value: Any,
            ttl: int = 300
    ):
        await self.client.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str, ):
        await self.client.delete(key)

    async def get_pattern(self, pattern: str):
        keys = await self.client.keys(pattern)
        if keys:
            await self.client.delete(*keys)

    async def close(self):
        await self.client.aclose()

    async def add_to_blacklist(self,jti: str,ttl: int):
        key = f"blacklist:{jti}"
        await self.client.setex(key, ttl, "1")

async def get_redis_client() -> Redis:
    return Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )


RedisDep = Annotated[
    Redis,
    Depends(get_redis_client)
]


async def get_cache_service(
        redis: RedisDep,
) -> CacheService:
    return CacheService(redis)


CacheServiceDep = Annotated[
    CacheService,
    Depends(get_cache_service)
]