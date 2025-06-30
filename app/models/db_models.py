from datetime import datetime
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    def __repr__(self):
        __allow_unmapped__ = True
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return f"{self.__class__.__name__}({data})"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(nullable=True)
    last_name: Mapped[str | None] = mapped_column(nullable=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    joined_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Связь с привычками
    habits: Mapped[List['HabitModel']] = relationship(back_populates="owner",  cascade="all, delete-orphan")


class HabitModel(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True, nullable=False)
    frequency: Mapped[str | None] = mapped_column(nullable=True)
    goal_days: Mapped[int | None] = mapped_column(nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # Связь с владельцем
    owner: Mapped['UserModel'] = relationship(back_populates="habits", cascade="save-update")

    # Связь с историей выполнения
    trackings: Mapped[List['TrackingModel']] = relationship(back_populates="habit",  cascade="all, delete-orphan")


class TrackingModel(Base):
    __tablename__ = "trackings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    was_performed: Mapped[bool] = mapped_column(default=False)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"))

    # Связь с привычкой
    habit: Mapped['HabitModel'] = relationship(back_populates="trackings")
