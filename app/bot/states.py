from aiogram.fsm.state import StatesGroup, State


class CommonState(StatesGroup):
    # Токен JWT
    token = State()

class AddHabitStates(StatesGroup):
    # Состояния для добавления привычки
    title = State()
    frequency = State()
    goal_days = State()

class EditHabitStates(StatesGroup):
    # Состояния для редактирования привычки
    title = State()
    frequency = State()
    goal_days = State()
    original_title = State()