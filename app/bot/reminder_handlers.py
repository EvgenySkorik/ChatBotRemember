from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.api.router import add_tracking
from app.bot.exceptions_handlers import InvalidInputError
from app.bot.messages import MU
from app.services.loging import get_logger

reminder_router = Router()
logger = get_logger("reminder_logger")


@reminder_router.callback_query(F.data.startswith("reminder_"))
async def handle_reminder_response(call: CallbackQuery):
    """Обработчик inline кнопок напоминания о привычке
    yes - запускает добавление трека, если завершен удаляет
    no - выводит сообщение о необходимости выполнить"""
    try:
        _, action, habit_title = call.data.split("_", 2)
        if action == "yes":
            await call.answer(MU.habit_remind(habit_title))

            result, is_completed = await add_tracking(
                habit_title=habit_title,
                telegram_id=call.from_user.id
            )

            if is_completed:
                await call.message.answer(MU.habit_finished(habit_title))

        else:
            await call.answer(MU.habit_dont_forget1())
            await call.message.answer(MU.habit_dont_forget2(habit_title))

        await call.message.delete()

    except InvalidInputError as e:
        await call.answer(MU.try_again_later(e))
