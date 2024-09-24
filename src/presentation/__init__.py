from fastapi import FastAPI

from src.presentation.routers.chat import router as chat_router
from src.presentation.routers.search import router as search_router

routers = [
    chat_router,
    search_router,
]


def register_routers(app: FastAPI):
    for router in routers:
        app.include_router(router)
