from typing import List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.api.router import add_habit, get_all_habits_by_user
from app.bot.exceptions_handlers import InvalidInputError
from app.bot.keyboards import ReplyKeyboardRep, InlineKeyboardRep
from app.bot.messages import MU
from app.models.shemas import HabitShema, HabitShemaOUT
from app.services.loging import get_logger
from app.bot.states import AddHabitStates
from app.services.scheduler import schedule_habit

logger = get_logger("add_habit_bot_loger")
add_habit_router = Router()


@add_habit_router.message(F.text.contains("📝 ДОБАВИТЬ ПРИВЫЧКУ"))
async def handle_add_habit(message: Message, state: FSMContext):
    """Запуск скрипта по добавлению привычки Обработчик пункта меню"""
    st = await state.get_data()
    await message.answer(MU.answer_message(message.text), parse_mode=MU.MD)
    await state.set_state(AddHabitStates.title)
    await message.answer(MU.habit_create_name(), parse_mode=MU.HTML)


@add_habit_router.message(AddHabitStates.title)
async def process_get_habit_name(message: Message, state: FSMContext):
    """Обработчик получения названия привычки"""
    try:
        habits: List[HabitShemaOUT] = await get_all_habits_by_user(message.from_user.id)
        existing_habit = [habit for habit in habits if habit.title.lower() == message.text.lower()]

        if not existing_habit:
            await state.update_data(title=message.text)
            await state.set_state(AddHabitStates.frequency)

            await message.answer(
                MU.habit_create_frequency(),
                parse_mode=MU.HTML,
                reply_markup=InlineKeyboardRep.frequency_keyboard()
            )

        else:
            await message.answer(MU.habit_exist())
    except InvalidInputError as e:
        await message.answer(MU.wrong_input(e.user_message))


@add_habit_router.callback_query(lambda call: call.data.startswith("freq_"))
async def handle_number_selection(call: CallbackQuery, state: FSMContext):
    """Обработчик получения для выбора частоты"""
    partial_choice = call.data.split("_")[1:]

    if partial_choice[0] == "num":
        await state.update_data(frequency_number=partial_choice[1])
        await call.answer(MU.answer_message(partial_choice[1]))

    elif partial_choice[0] == "unit":
        data = await state.get_data()
        full_string = f"{data['frequency_number']} в {partial_choice[1]}"
        await state.update_data(frequency=full_string)

        await call.answer(MU.answer_message(partial_choice[1]))
        await call.message.edit_reply_markup(None)
        await state.set_state(AddHabitStates.goal_days)
        await call.message.answer(
            MU.habit_create_goal_days(),
            parse_mode=MU.HTML
        )


@add_habit_router.message(AddHabitStates.goal_days)
async def process_get_goal_days(message: Message, state: FSMContext):
    """Обработчик получения для формирования количества дней
       Запуск функции добавления в базу сформированной модели привычки"""
    try:
        if message.text.isdigit():
            await state.update_data(goal_days=message.text)
            data = await state.get_data()

            habit_model = await add_habit(
                habit_data=HabitShema.model_validate(data),
                telegram_id=message.from_user.id
            )

            await schedule_habit(
                habit_id=habit_model.id,
                chat_id=message.from_user.id,
                habit_title=habit_model.title,
                frequency=habit_model.frequency
            )

            token = (await state.get_data()).get('token')
            await state.clear()
            await state.update_data(token=token)

            await message.answer(
                MU.habit_adedd(),
                reply_markup=ReplyKeyboardRep.start_keyboard()
            )
        else:
            await message.answer(MU.habit_goal_days_is_digit())

    except InvalidInputError as e:
        await message.answer(MU.wrong_input2(e.user_message))
