from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.conf import settings
from app.models.db_models import Base

engine = create_async_engine(settings.URL, echo=False)
AsyncSession = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

