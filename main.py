from fastapi import FastAPI
from src.presentation import register_routers
from src.presentation.utils import app_lifespan, lifespan_redis

from config import settings


app = FastAPI(
    root_path="/api",
    lifespan=app_lifespan(
        lifespans=[lifespan_redis],
    ),
)
register_routers(app)


def main():
    import uvicorn

    kwargs = dict(
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True,
    )

    uvicorn.run("main:app", **kwargs)

if __name__ == "__main__":
    main()
