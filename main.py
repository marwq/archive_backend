from fastapi import FastAPI
from src.presentation import register_routers

from config import settings


app = FastAPI(
    root_path="/api",
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
