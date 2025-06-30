from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.api.router import get_all_habits_by_user, get_habit, delete_habit
from app.bot.exceptions_handlers import NotFoundError
from app.bot.keyboards import InlineKeyboardRep
from app.bot.messages import MU
from app.services.loging import get_logger

logger = get_logger("list_habits_loger")
list_habits_router = Router()


@list_habits_router.message(F.text.contains("📋 СПИСОК ПРИВЫЧЕК"))
async def handle_list_habits(message: Message):
    """Запуск скрипта по списку привычек Обработчик пункта меню"""
    await message.answer(MU.answer_message(message.text), parse_mode=MU.MD)
    habits = await get_all_habits_by_user(message.from_user.id)
    if habits:
        keyboard = InlineKeyboardRep.habits_keyboard(habits)
        await message.answer(
            MU.message_list(),
            reply_markup=keyboard,
            parse_mode=MU.HTML
        )

@list_habits_router.callback_query(lambda call: call.data.startswith("detail_"))
async def edit_habit_callback(call: CallbackQuery):
    """Выводит подробную информацию о привычке"""
    habit_title = call.data.replace("detail_", "")
    await call.answer(f"Подробно про привычку: {habit_title}")
    habit = await get_habit(title=habit_title, telegram_id=call.from_user.id)
    await call.message.answer(MU.send_habit_details(habit), MU.HTML)

@list_habits_router.callback_query(lambda call: call.data.startswith("delete_"))
async def delete_habit_callback(call: CallbackQuery):
    """Удаление привычки"""
    try:
        habit_title = call.data.replace("delete_", "")
        await call.answer(f"Удалить привычку: {habit_title}")
        await call.message.answer(habit_title)
        del_habit = await delete_habit(habit_data=habit_title, telegram_id=call.from_user.id)
        await call.message.answer(MU.habit_deleted(habit_title))
    except NotFoundError as e:
        await call.message.answer(MU.habit_deleted(e))