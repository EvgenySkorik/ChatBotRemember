import asyncio

import uvicorn
from fastapi import FastAPI

from app.api.router import lifespan, router_users, router_habits, router_trackings
from app.conf import settings
from app.services.loging import get_logger
from database.database import create_tables
from app.models.db_bot_models import init_db

logger = get_logger("create_app_logger")

def create_app() -> FastAPI:
    """Создание экземпляра FastAPI"""
    app = FastAPI(**settings.FASTAPI_CONFIG, lifespan=lifespan)
    app.include_router(router_users)
    app.include_router(router_habits)
    app.include_router(router_trackings)
    return app

async def setup_database():
    """Создание таблиц перед запуском приложения"""
    try:
        await create_tables()
        logger.info("Таблицы в базе данных успешно созданы")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise

async def run_server():
    """Запуск сервера"""
    # await setup_database()
    await init_db()

    config = uvicorn.Config(app, host=settings.UVICORN_HOST, port=settings.UVICORN_PORT, reload=True, log_level="debug")
    server = uvicorn.Server(config=config)
    await server.serve()

app = create_app()

logger.info("Экземпляр FastAPI создан - app")

if __name__ == "__main__":
    asyncio.run(run_server())