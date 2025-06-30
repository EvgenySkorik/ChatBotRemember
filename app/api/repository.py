from datetime import datetime, timedelta
from time import sleep
from typing import Optional, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.bot.exceptions_handlers import DatabaseError
from app.models.db_models import UserModel, HabitModel, TrackingModel
from app.models.shemas import UserShema, RegistrationUserShema, HabitShema, HabitShemaOUT, TrackingShemaOUT, \
    UserShemaOUT, UserCreate
from sqlalchemy import select, func

from app.services.loging import get_logger
from app.services.scheduler import remove_habit_reminder
from app.utils.utils import create_user_model
from database.database import AsyncSession

logger = get_logger("Repository_logger")


class UserRep:
    @classmethod
    async def registration_user(cls, data: RegistrationUserShema) -> int:
        """
        Добавляем в базу пользователя если его нет, response: user.id
        используем при первом входе для проверки и регистрации пользователя
        """
        async with AsyncSession() as session:

            stmt = select(UserModel.id).where(UserModel.telegram_id == data.telegram_id)
            user_check = (await session.execute(stmt)).scalar_one_or_none()
            if user_check:
                return user_check

            user = UserModel(**data.model_dump())
            session.add(user)
            logger.info(f"Пользователь id={user.id} name={user.first_name} успешно зарегистрирован.")

            try:
                await session.flush()
                await session.commit()
                logger.info(f"Добавлен пользователь id={user_check}")
                return user.telegram_id
            except IntegrityError as ex:
                await session.rollback()
                logger.error(f"Ошибка интеграции в базу {ex}")
                raise DatabaseError(f"Ошибка интеграции в базу: {ex}")


    @classmethod
    async def add_user(cls, data: UserShema) -> int:
        """Добавляем в базу пользователя если его нет, response: user.id"""
        stmt = select(UserModel.id).where(UserModel.telegram_id==data.telegram_id)

        async with AsyncSession() as session:
            user_exist = (await session.execute(stmt)).scalar_one_or_none()
            if  user_exist:
                return user_exist
            user = UserModel(**data.model_dump())
            session.add(user)

            try:
                await session.flush()
                await session.commit()
                logger.info(f"Добавлен пользователь id={user.id}")
                return user.id
            except IntegrityError as ex:
                await session.rollback()
                raise DatabaseError(f"Ошибка интеграции в базу: {ex}")


    @classmethod
    async def get_all_users(cls) -> Optional[List[UserShemaOUT] | None]:
        """Получить из базы список всех пользователей если есть"""

        async with AsyncSession() as session:
            stmt_user = (
                select(UserModel)
                .options(
                    selectinload(UserModel.habits)
                    .selectinload(HabitModel.trackings)
                )
            )
            users = (await session.execute(stmt_user)).scalars().all()
            if not users:
                return None

            return [UserShemaOUT.model_validate(u, from_attributes=True) for u in users]


class HabitRep:
    @classmethod
    async def add_habit(cls, habit: HabitShema, telegram_id) -> Optional[HabitShemaOUT]:
        """Добавляем в базу пользователю привычку если её нет, response: habit"""

        async with AsyncSession() as session:
            stmt_user = select(UserModel).where(UserModel.telegram_id == telegram_id
                                                ).options(selectinload(UserModel.habits))
            stmt_habit = select(HabitModel).where(HabitModel.title == habit.title
                                                  ).options(selectinload(HabitModel.trackings))

            user: UserModel = (await session.execute(stmt_user)).scalar_one_or_none()
            check_habit = (await session.execute(stmt_habit)).scalar_one_or_none()

            if user and not check_habit:
                habit.owner_id = user.id
                dump = habit.model_dump()
                habit_mod = HabitModel(**dump)
                user.habits.append(habit_mod)
                session.add(habit_mod)

                try:
                    logger.info(f"Добавлена привычка habit={habit_mod.title} к user={user.first_name}")
                    await session.commit()
                    await session.refresh(habit_mod)
                    habit_shema = (await session.execute(stmt_habit)).scalar_one_or_none()
                    return HabitShemaOUT.model_validate(habit_shema, from_attributes=True)
                except IntegrityError as ex:
                    await session.rollback()
                    logger.ERROR(f"Ошибка интеграции в базу {ex}")
                    raise ValueError(f"Ошибка интеграции в базу: {ex}")
            else:
                logger.info(f"Пользователь с telegram_id={telegram_id} не найден")
                return None

    @classmethod
    async def delete_habit(cls, habit: str, telegram_id: int) -> str:
        """Удаляем из базы привычку если есть"""
        logger.info(F"HABIT {habit} id {telegram_id}")
        async with AsyncSession() as session:
            stmt_user = (
                select(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .options(selectinload(UserModel.habits))
            )
            user: UserModel = (await session.execute(stmt_user)).scalar_one_or_none()

            habit_to_delete = next(
                (h for h in user.habits if h.title == habit),
                None
            )

            if not habit_to_delete:
                logger.warning(f"Привычка '{habit}' не найдена у пользователя {user.first_name}")
                return f"Привычка '{habit}' не найдена!"


            await session.delete(habit_to_delete)
            await session.commit()

            logger.info(f"Привычка '{habit}' успешно удалена у пользователя {user.first_name}")
            return habit

    @classmethod
    async def get_all_habits_by_user(cls, telegram_id: int) -> List[HabitShemaOUT]:
        """Получить из базы список всех привычек пользователя если есть, response: List[HabitShemaOUT]"""

        async with AsyncSession() as session:
            stmt_user = (
                select(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .options(
                    selectinload(UserModel.habits)
                    .selectinload(HabitModel.trackings)
                )
            )
            user = (await session.execute(stmt_user)).scalar_one_or_none()

            return [
                HabitShemaOUT.model_validate(habit, from_attributes=True)
                for habit in (user.habits if user else [])
            ]

    @classmethod
    async def get_habit(cls, habit_title: str, telegram_id: int) -> Optional[HabitShemaOUT]:
        """Получить из базы привычку пользователя если есть, response: HabitShemaOUT"""

        async with AsyncSession() as session:
            stmt_user = (
                select(UserModel).where(UserModel.telegram_id == telegram_id)
                .options(selectinload(UserModel.habits)
                         .options(selectinload(HabitModel.trackings)))
            )
            user = (await session.execute(stmt_user)).scalar_one_or_none()

            stmt_habit = (
                select(HabitModel)
                .where(HabitModel.title == habit_title, HabitModel.owner_id == user.id)
                .options(selectinload(HabitModel.trackings))
            )

            habit = (await session.execute(stmt_habit)).scalar_one_or_none()

            try:
                return HabitShemaOUT.model_validate(habit, from_attributes=True)
            except AttributeError as ex:
                return None

    @classmethod
    async def update_habit(cls, title: str, habit_data: HabitShema, telegram_id) -> Optional[HabitShemaOUT]:
        """Обновляем в базе пользователю привычку если её нет, response: habit"""
        async with AsyncSession() as session:
            user = await session.execute(
                select(UserModel.id).where(UserModel.telegram_id == telegram_id)
            )

            user_id = user.scalar_one_or_none()

            stmt_habit = (
                select(HabitModel)
                .where(HabitModel.owner_id == user_id, HabitModel.title == title)
                .options(selectinload(HabitModel.trackings)
                         )
            )
            habit_mod: HabitModel = (await session.execute(stmt_habit)).scalar_one_or_none()

            habit_mod.title = habit_data.title
            habit_mod.goal_days = habit_data.goal_days
            habit_mod.frequency = habit_data.frequency

            try:
                await session.commit()
                return HabitShemaOUT.model_validate(habit_mod, from_attributes=True)

            except IntegrityError as ex:
                await session.rollback()
                logger.ERROR(f"Ошибка интеграции в базу {ex}")
                raise ValueError(f"Ошибка интеграции в базу: {ex}")

    @classmethod
    async def get_remaining_today(cls, user_id: int, habit_title: str, count_str: str) -> int:
        """Возвращает сколько раз еще можно отметить сегодня"""
        count_limits = {"один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5}
        max_allowed = count_limits.get(count_str, 1)

        async with AsyncSession() as session:
            today_start = datetime.now().replace(hour=0, minute=0, second=0)

            current_count = await session.execute(
                select(func.count(TrackingModel.id))
                .join(HabitModel)
                .where(
                    HabitModel.owner_id == user_id,
                    HabitModel.title == habit_title,
                    TrackingModel.date >= today_start
                )
            )

            return max(0, max_allowed - current_count.scalar())


class TrackingsRep:
    @classmethod
    async def add_tracking(cls, habit_title: str, telegram_id: int) -> tuple[TrackingShemaOUT | None, bool]:
        """Добавляем в базу трек если нет"""

        async with AsyncSession() as session:
            try:
                user = await session.execute(
                    select(UserModel.id).where(UserModel.telegram_id == telegram_id)
                )

                user_id = user.scalar_one_or_none()

                stmt_habit = (
                    select(HabitModel)
                    .where(HabitModel.owner_id == user_id, HabitModel.title == habit_title)
                    .options(selectinload(HabitModel.trackings)
                             )
                )
                habit_mod: HabitModel = (await session.execute(stmt_habit)).scalar_one_or_none()

                if habit_mod.frequency and not await cls._check_frequency_limit(session, habit_mod):
                    return None, False

                tracking = TrackingModel(
                    habit_id=habit_mod.id,
                    was_performed=True
                )

                session.add(tracking)
                habit_mod.trackings.append(tracking)

                await session.commit()
                await session.refresh(tracking)
                logger.info(f"Трек {tracking.id} добавлен к привычке {habit_mod.title} у пользователя {user_id}")

                trackings_count = await session.execute(
                    select(func.count(TrackingModel.id))
                    .where(TrackingModel.habit_id == habit_mod.id)
                )
                current_count = trackings_count.scalar()
                is_completed = current_count >= habit_mod.goal_days

                logger.info(f"Трекингов: {current_count}, цель: {habit_mod.goal_days}, завершена: {is_completed}")

                if is_completed:
                    logger.info(f"Привычка {habit_title} завершена!")
                    await remove_habit_reminder(habit_mod.id)
                    await HabitRep.delete_habit(habit_title, telegram_id)

                result = TrackingShemaOUT.model_validate(tracking, from_attributes=True)
                if not result:
                    logger.error("Ошибка валидации трекинга")

                return result, is_completed

            except Exception as e:
                logger.error(f"Ошибка в add_tracking: {str(e)}", exc_info=True)
                await session.rollback()
                return None, False

    @staticmethod
    async def _check_frequency_limit(session: AsyncSession, habit: HabitModel) -> bool:
        """Проверяет, можно ли добавить трекинг, учитывая лимиты"""
        if not habit.frequency:
            return True

        count_str, _, period = habit.frequency.partition(" в ")
        count_limits = {"один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5}
        max_allowed = count_limits.get(count_str, 1)

        now = datetime.now()

        period_starts = {
            "день": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "неделю": now - timedelta(days=now.weekday()),
            "месяц": now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            "квартал": now.replace(
                month=((now.month - 1) // 3) * 3 + 1,
                day=1, hour=0, minute=0, second=0, microsecond=0
            ),
            "год": now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
        }
        period_start = period_starts.get(period)
        if not period_start:
            return True

        current_count = (await session.execute(
            select(func.count(TrackingModel.id))
            .where(
                TrackingModel.habit_id == habit.id,
                TrackingModel.date >= period_start
            )
        )).scalar() or 0

        return current_count < max_allowed
