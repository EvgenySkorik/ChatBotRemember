from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.models.shemas import HabitShemaOUT


class ReplyKeyboardRep:
    @classmethod
    def start_keyboard(cls):
        """Генерация Reply-клавиатуры для стартового меню"""
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📝 ДОБАВИТЬ ПРИВЫЧКУ"), KeyboardButton(text="📋 СПИСОК ПРИВЫЧЕК")]
            ],
            resize_keyboard=True
        )
        return keyboard


class InlineKeyboardRep:
    @classmethod
    def habits_keyboard(cls, habits):
        """Генерация inline-клавиатуры на основе списка привычек"""
        buttons = []
        for habit in habits:
            long_button = InlineKeyboardButton(
                text=f"📌 {habit.title.upper()}\n({habit.frequency.lower()} × {habit.goal_days})",
                callback_data=f"detail_{habit.title}" #Привычка
            )
            buttons.append([long_button])

            action_buttons = [
                InlineKeyboardButton(text="✅", callback_data=f"mark_{habit.title}"),  # Отметить
                InlineKeyboardButton(text="✏️", callback_data=f"edit_{habit.title}"),  # Редактировать
                InlineKeyboardButton(text="🗑️", callback_data=f"delete_{habit.title}")  # Удалить
            ]

            buttons.append(action_buttons)

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    @classmethod
    def frequency_keyboard(cls):
        """Строит inline-клавиатуру для выбора частоты привычки"""
        numbers = ["один", "два", "три", "четыре", "пять"]
        units = ["день", "неделю", "месяц", "квартал", "год"]

        # Создаем кнопки
        buttons = []
        for num, unit in zip(numbers, units):
            left_button = InlineKeyboardButton(text=num, callback_data=f"freq_num_{num}")
            middle_button = InlineKeyboardButton(text="в", callback_data="no_action")
            right_button = InlineKeyboardButton(text=unit, callback_data=f"freq_unit_{unit}")

            buttons.append([left_button, middle_button, right_button])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    @classmethod
    def frequency_keyboard_by_update(cls):
        """Строит inline-клавиатуру для выбора частоты привычки"""
        numbers = ["один", "два", "три", "четыре", "пять"]
        units = ["день", "неделю", "месяц", "квартал", "год"]

        buttons = []
        for num, unit in zip(numbers, units):
            left_button = InlineKeyboardButton(text=num, callback_data=f"update-freq_num_{num}")
            middle_button = InlineKeyboardButton(text="в", callback_data="no_action")
            right_button = InlineKeyboardButton(text=unit, callback_data=f"update-freq_unit_{unit}")

            buttons.append([left_button, middle_button, right_button])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    @classmethod
    def reminder_keyboard(cls, habit_title):
        """Строит inline-клавиатуру для выбора ответа для планировщика"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"reminder_yes_{habit_title}"),
                InlineKeyboardButton(text="❌ Нет", callback_data=f"reminder_no_{habit_title}")
            ]
        ])
        return keyboard



