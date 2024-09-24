import os
from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncIterator, List

from fastapi import FastAPI

from src.application.redis import redis_client



def app_lifespan(lifespans: List):
    @asynccontextmanager
    async def _lifespan_manager(app: FastAPI):
        exit_stack = AsyncExitStack()
        async with exit_stack:
            for lifespan in lifespans:
                await exit_stack.enter_async_context(lifespan(app))
            yield

    return _lifespan_manager

@asynccontextmanager
async def lifespan_redis(app: FastAPI) -> AsyncIterator[None]:
    await redis_client.connect()
    yield
    await redis_client.close()