from fastapi import APIRouter, Depends, FastAPI, Query, Body
from typing import Annotated, List
from contextlib import asynccontextmanager

from app.api.repository import UserRep, HabitRep, TrackingsRep
from app.models.shemas import UserShema, RegistrationUserShema, HabitShema, HabitShemaOUT, TrackingShemaOUT, \
    UserShemaOUT
from app.services.security import AuthService
from app.services.loging import get_logger

logger = get_logger("roter_logger")


router_users = APIRouter(
    prefix="/user",
    tags=["Пользователи"],
)

router_habits = APIRouter(
    prefix="/habit",
    tags=["Привычки"],
)

router_trackings = APIRouter(
    prefix="/tracking",
    tags=["Отслеживание"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Запуск')
    # await delete_tables()
    # await create_tables()
    yield
    # await session.close()
    # await engine.dispose()
    print('Отключение')


AuthDEP = Depends(AuthService.verify_token_fastapi)

# Ручки по пользователю


@router_users.post("/registration", summary="Регистрация")
async def registration_user(user: Annotated[RegistrationUserShema, Depends()]) -> int:
    """Регистрируем и добавляем пользователя"""
    user_id = await UserRep.registration_user(user)
    return user_id

@router_users.post("/add", summary="Добавить")
async def add_user(
        user: UserShema
) -> int:
    """Добавляем пользователя"""

    user_id = await UserRep.add_user(user)
    return user_id

# Ручки по привычкам

@router_habits.post("/add", summary="Добавить", dependencies=[AuthDEP])
async def add_habit(
        habit_data: HabitShema,
        telegram_id: int
) -> HabitShemaOUT:
    """Добавляем привычку"""
    habit = await HabitRep.add_habit(habit_data, telegram_id)
    return habit

@router_habits.get("/habits", summary="Список", dependencies=[AuthDEP])
async def get_all_habits_by_user(
        telegram_id: int = Query(..., description="Telegram ID пользователя")
) -> List[HabitShemaOUT]:
    """Получить список привычек"""
    habits = await HabitRep.get_all_habits_by_user(telegram_id)
    return habits

@router_habits.get("/habit", summary="Привычка", dependencies=[AuthDEP])
async def get_habit(
        title: str = Query(..., description="Наименование привычки"),
        telegram_id: int = Query(..., description="Telegram ID пользователя")
) -> HabitShemaOUT:
    """Получить привычку"""
    habit = await HabitRep.get_habit(habit_title=title, telegram_id=telegram_id)
    return habit

@router_habits.delete("/delete", summary="Удалить", dependencies=[AuthDEP])
async def delete_habit(
        habit_data: str = Query(..., description="Наименование привычки"),
        telegram_id: int = Query(..., description="Telegram ID пользователя")
) -> str:
    """Удаляем привычку"""
    habit = await HabitRep.delete_habit(habit_data, telegram_id)
    return habit

@router_habits.put("/update", summary="Обновить", dependencies=[AuthDEP])
async def update_habit(
        title: str = Query(..., description="Наименование привычки"),
        habit_data: HabitShema = Body(..., description="Данные для обновления привычки"),
        telegram_id: int = Query(..., description="Telegram ID пользователя")
) -> HabitShemaOUT:
    """Обновляем привычку"""
    habit = await HabitRep.update_habit(title, habit_data, telegram_id)
    return habit

# Ручки по отслеживанию
@router_trackings.post("/add", summary="Добавить", dependencies=[AuthDEP])
async def add_tracking(
        habit_title: str = Query(..., description="Наименование привычки"),
        telegram_id: int = Query(..., description="Telegram ID пользователя")
) -> tuple[TrackingShemaOUT | None, bool]:
    """Добавляем трек"""
    track = await TrackingsRep.add_tracking(habit_title, telegram_id)
    return track

