from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.api.repository import HabitRep
from app.api.router import add_tracking, get_habit
from app.bot.exceptions_handlers import NotFoundError, DatabaseError, InvalidInputError
from app.bot.keyboards import ReplyKeyboardRep
from app.bot.messages import MU
from app.models.shemas import TrackingShemaOUT
from app.services.loging import get_logger

logger = get_logger("trackings_habit_loger")
trackings_router = Router()


@trackings_router.callback_query(F.data.startswith("mark_"))
async def edit_habit_callback(call: CallbackQuery):
    """Обработчик кнопки отметки выполнения привычки
        Запуск скрипта выполнения привычки"""
    habit_title = call.data.replace("mark_", "")
    user_id = call.from_user.id

    try:
        habit = await get_habit(habit_title, user_id)
        if not habit:
            raise NotFoundError("привычка")

        result, is_completed = await add_tracking(habit_title, user_id)

        if is_completed:
            await call.answer(MU.habit_done_and_deleted(habit_title))
            await call.message.answer(
                text=MU.habit_congratulations(habit_title),
                parse_mode=MU.HTML,
                reply_markup=ReplyKeyboardRep.start_keyboard()
            )
            return

        if result is not None:
            await call.answer(MU.habit_remind(habit_title))

            if habit.frequency:
                count_str, _, period = habit.frequency.partition(" в ")
                remaining = await HabitRep.get_remaining_today(user_id, habit_title, count_str)
                if remaining > 0:
                    await call.message.answer(MU.count_remind(remaining))
            return

        await call.answer(
            MU.habit_limit_error(habit_title, habit.frequency),
            show_alert=True
        )

    except InvalidInputError as e:
        await call.answer(f"🛑 {e.user_message}", show_alert=True)
