from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.messages import MU
from app.services.loging import get_logger
from app.bot.api_client import call_api
from app.services.scheduler import remove_habit_reminder

logger = get_logger("trackings_habit_loger")
trackings_router = Router()


@trackings_router.callback_query(F.data.startswith("mark_"))
async def edit_habit_callback(call: CallbackQuery, state: FSMContext):
    """Обработчик кнопки отметки выполнения привычки
        Запуск скрипта выполнения привычки, удаляет cron"""
    habit_title = call.data.replace("mark_", "")
    token = (await state.get_data()).get("token")
    try:
        response = await call_api(
            method="POST",
            endpoint="/tracking/add",
            data={"habit_title": habit_title, "telegram_id": call.from_user.id},
            token=token
        )
        logger.info(f"RESP IN mark{response}")
        if response.get("result"):
            await call.answer(MU.habit_remind(habit_title))
            if response.get("is_completed"):
                await call.message.answer(MU.habit_finished(habit_title))
                await remove_habit_reminder(response.get("result").get("habit_id"))
        else:
            await call.answer(
                MU.habit_limit_error(habit_title, response.get('limit', '')),
                show_alert=True
            )

    except Exception as e:
        logger.error(f"Mark error: {str(e)}")
        await call.answer("Ошибка при отметке", show_alert=True)
