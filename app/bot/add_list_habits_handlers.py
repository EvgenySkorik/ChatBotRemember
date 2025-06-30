from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot.exceptions_handlers import NotFoundError
from app.bot.keyboards import InlineKeyboardRep
from app.bot.messages import MU
from app.services.loging import get_logger
from app.bot.api_client import call_api
from app.models.db_models import HabitModel
from app.models.shemas import HabitShemaOUT

logger = get_logger("list_habits_loger")
list_habits_router = Router()


@list_habits_router.message(F.text.contains("📋 СПИСОК ПРИВЫЧЕК"))
async def handle_list_habits(message: Message, state: FSMContext):
    """Запуск скрипта по списку привычек Обработчик пункта меню"""
    await message.answer(MU.answer_message(message.text), parse_mode=MU.MD)

    token = (await state.get_data()).get("token")
    habits_d = await call_api(
        method="GET",
        endpoint=f"/habit/habits?telegram_id={message.from_user.id}",
        token=token
    )

    habits_d_shema = [HabitShemaOUT.model_validate(habit, from_attributes=True) for habit in habits_d]

    habits = [HabitModel(**h.model_dump(exclude={"trackings"})) for h in habits_d_shema]

    if habits:
        keyboard = InlineKeyboardRep.habits_keyboard(habits)
        await message.answer(
            MU.message_list(),
            reply_markup=keyboard,
            parse_mode=MU.HTML
        )

@list_habits_router.callback_query(lambda call: call.data.startswith("detail_"))
async def edit_habit_callback(call: CallbackQuery, state: FSMContext):
    """Выводит подробную информацию о привычке"""
    habit_title = call.data.replace("detail_", "")
    await call.answer(f"Подробно про привычку: {habit_title}")

    token = (await state.get_data()).get("token")
    habit_d = await call_api(
        method="GET",
        endpoint=f"/habit/habit?title={habit_title}&telegram_id={call.from_user.id}",
        token=token
    )
    habit = HabitModel(**habit_d)

    await call.message.answer(MU.send_habit_details(habit), MU.HTML)

@list_habits_router.callback_query(lambda call: call.data.startswith("delete_"))
async def delete_habit_callback(call: CallbackQuery, state: FSMContext):
    """Удаление привычки"""
    try:
        habit_title = call.data.replace("delete_", "")
        await call.answer(f"Удалить привычку: {habit_title}")
        await call.message.answer(habit_title)

        token = (await state.get_data()).get("token")
        habit_d = await call_api(
            method="DELETE",
            endpoint=f"/habit/delete?habit_data={habit_title}&telegram_id={call.from_user.id}",
            token=token
        )

        await call.message.answer(MU.habit_deleted(habit_title))
    except NotFoundError as e:
        await call.message.answer(MU.habit_deleted(e))