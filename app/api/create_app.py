import uvicorn
from fastapi import FastAPI

from app.api.router import lifespan, router_users, router_habits, router_trackings
from app.conf import settings
from app.services.loging import get_logger

logger = get_logger("create_app_logger")

def create_app() -> FastAPI:
    """Создание экземпляра FastAPI"""
    app = FastAPI(**settings.FASTAPI_CONFIG, lifespan=lifespan)
    app.include_router(router_users)
    app.include_router(router_habits)
    app.include_router(router_trackings)
    return app

async def run_server():
    config = uvicorn.Config(app, host=settings.UVICORN_HOST, port=settings.UVICORN_PORT, reload=True)
    server = uvicorn.Server(config=config)
    await server.serve()

app = create_app()
logger.info("Экземпляр FastAPI создан - app")