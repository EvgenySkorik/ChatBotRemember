from pathlib import Path
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.conf import settings
from app.models.db_models import Base


engine = create_async_engine(settings.URL, echo=False)
AsyncSession = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

Path("/data").mkdir(exist_ok=True)
async_db_url = settings.URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
engine_bot = create_async_engine(async_db_url, echo=False)
AsyncSessionBot = async_sessionmaker(
    bind=engine_bot,
    expire_on_commit=False
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

