from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from database.database import engine_bot


class Base(DeclarativeBase):
    def __repr__(self):
        __allow_unmapped__ = True
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return f"{self.__class__.__name__}({data})"


class BotToken(Base):
    __tablename__ = "bot_token"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    token: Mapped[int] = mapped_column(unique=True, nullable=False)


async def init_db():
    async with engine_bot.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)