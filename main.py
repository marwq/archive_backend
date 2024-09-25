from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.presentation import register_routers
from src.presentation.utils import app_lifespan, lifespan_redis
from config import settings


app = FastAPI(
    root_path="/api",
    lifespan=app_lifespan(
        lifespans=[lifespan_redis],
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любых источников
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)
from loguru import logger
logger.info("cors")
register_routers(app)


def main():

    import uvicorn

    kwargs = dict(
        host="0.0.0.0",
        port=settings.APP_PORT,
        workers=4,
    )

    uvicorn.run("main:app", **kwargs)


if __name__ == "__main__":
    main()
