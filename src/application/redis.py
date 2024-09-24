from typing import Any
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from redis import asyncio as aioredis

from config import settings

load_dotenv()


class RedisClient:
    _instance = None

    def __new__(cls, redis_url: str):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance.redis_url = redis_url
        return cls._instance

    async def get(self, key: str):
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self, key: str, value: dict, expire: int = 3600, expire_at: datetime | None = None
    ):
        value_str = json.dumps(value)
        if expire:
            await self.redis.set(key, value_str, ex=expire)
            return
        await self.redis.set(key, value_str)
        if expire_at:
            await self.redis.expireat(key, expire_at)

    async def incr_and_expireat(self, key: str, amount: int = 1, expire: datetime = None):
        count = await self.redis.incr(key, amount)
        await self.redis.expireat(key, expire)
        return count

    async def incr_and_expire(self, key: str, amount: int = 1, expire: int = 1):
        count = await self.redis.incr(key, amount)
        await self.redis.expire(key, time=expire)
        return count

    async def sismember(self, name: str, value: Any) -> bool:
        value_str = json.dumps(value)
        return await self.redis.sismember(name, value_str)
    
    async def sadd(self, name: str, *values: list[Any]) -> int:
        return await self.redis.sadd(name, *(json.dumps(v) for v in values))
    
    async def srem(self, name: str, *values: list[Any]) -> int:
        return await self.redis.srem(name, *(json.dumps(v) for v in values))
    
    async def rpush(self, name: str, *values: list[Any]) -> None:
        await self.redis.rpush(name, *(json.dumps(v) for v in values))
        
    async def lpop(self, name: str, count: int | None = None) -> Any:
        response = await self.redis.lpop(name, count)
        if isinstance(response, list):
            return [json.loads(i) for i in response]
        elif response is not None:
            return json.loads(response)
    
    async def delete(self, key: str):
        await self.redis.delete(key)

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url)

    async def close(self):
        await self.redis.close()

    async def ping(self):
        await self.redis.ping()


redis_url = f"redis://:{settings.REDIS_PASS}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
redis_client = RedisClient(redis_url=redis_url)
# TODO move to DI layer
