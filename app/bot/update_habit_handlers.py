from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.api.router import update_habit
from app.bot.exceptions_handlers import InvalidInputError
from app.bot.keyboards import InlineKeyboardRep, ReplyKeyboardRep
from app.bot.messages import MU
from app.models.shemas import HabitShema
from app.services.loging import get_logger
from app.bot.states import EditHabitStates

logger = get_logger("update_habit_loger")
update_habit_router = Router()


@update_habit_router.callback_query(F.data.startswith("edit_"))
async def edit_habit_callback(call: CallbackQuery, state: FSMContext):
    """Обработчик кнопки редактирования привычки
    Запуск скрипта изменения привычки"""
    try:
        habit_title = call.data.replace("edit_", "")
        await state.update_data(original_title=habit_title)
        await call.answer(MU.habit_new_name(habit_title))

        await call.message.answer(MU.answer_message(MU.habit_update_name()), parse_mode=MU.HTML)
        await state.set_state(EditHabitStates.title)

    except InvalidInputError as e:
        await call.message.answer(MU.wrong_input(e.user_message))

@update_habit_router.message(EditHabitStates.title)
async def process_get_habit_name(message: Message, state: FSMContext):
    """Обработчик получения названия привычки"""

    await state.update_data(title=message.text)
    await state.set_state(EditHabitStates.frequency)

    await message.answer(
        MU.habit_create_frequency(),
        parse_mode=MU.HTML,
        reply_markup=InlineKeyboardRep.frequency_keyboard_by_update()
    )


@update_habit_router.callback_query(lambda call: call.data.startswith("update-freq_"))
async def handle_number_selection(call: CallbackQuery, state: FSMContext):
    """Обработчик получения для выбора частоты"""
    try:
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
            await state.set_state(EditHabitStates.goal_days)
            await call.message.answer(
                MU.habit_create_goal_days(),
                parse_mode=MU.HTML
            )
    except InvalidInputError as e:
        await call.message.answer(MU.wrong_input(e.user_message))

@update_habit_router.message(EditHabitStates.goal_days)
async def process_get_goal_days(message: Message, state: FSMContext):
    """Обработчик получения для формирования количества дней
       Запуск функции обновления в базе сформированной модели привычки"""
    try:
        if message.text.isdigit():
            await state.update_data(goal_days=message.text)

            data = await state.get_data()
            base_habit = data.get("original_title")

            habit_model = await update_habit(
                title=base_habit,
                habit_data=HabitShema.model_validate(data),
                telegram_id=message.from_user.id
            )

            token = (await state.get_data()).get('token')
            await state.clear()
            await state.update_data(token=token)

            await message.answer(
                MU.habit_updated(base_habit, habit_model.title),
                reply_markup=ReplyKeyboardRep.start_keyboard()
            )
        else:
            await message.answer(MU.habit_goal_days_is_digit())

    except InvalidInputError as e:
        await message.answer(MU.wrong_input(e.user_message))