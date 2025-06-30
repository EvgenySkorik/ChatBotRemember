from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.bot.messages import MU
from app.services.loging import get_logger
from app.bot.api_client import call_api
from app.services.scheduler import remove_habit_reminder

reminder_router = Router()
logger = get_logger("reminder_logger")


@reminder_router.callback_query(F.data.startswith("reminder_"))
async def handle_reminder_response(call: CallbackQuery, state: FSMContext):
    """Обработчик inline кнопок напоминания о привычке
    yes - запускает добавление трека, если завершен удаляет
    no - выводит сообщение о необходимости выполнить, удаляет cron"""
    try:
        _, action, habit_title = call.data.split("_", 2)
        token = (await state.get_data()).get("token")

        if action == "yes":
            response = await call_api(
                method="POST",
                endpoint="/tracking/add",
                data={"habit_title": habit_title, "telegram_id": call.from_user.id},
                token=token
            )

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
        else:
            await call.answer(MU.habit_dont_forget1())

        await call.message.delete()

    except Exception as e:
        logger.error(f"Reminder error: {str(e)}")
        await call.answer("Ошибка обработки", show_alert=True)
