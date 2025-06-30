from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from app.models.shemas import HabitShemaOUT


class MU:
    """Сообщения бота для пользователя"""
    MD = "MarkdownV2"
    HTML = "HTML"
    @classmethod
    def start_message(cls, data: Message) -> str:
        return (f'Приветствуем 😍 {data.from_user.first_name}!\n'
                f'Вы попали в бот трекера привычек! <b>"ChatBotRemember"</b>\n'
                f'<i>Воспользуйтесь меню внизу!</i>')

    @classmethod
    def token(cls, data) -> str:
        """Сообщения бота для пользователя Ваш токен"""
        return f"Твой токен для доступа к API:\n\n<b>{data}</b>"

    @classmethod
    def answer_message(cls, data) -> str:
        """Сообщения бота для пользователя Вы выбрали"""
        return f"*Вы выбрали {data}*"

    @classmethod
    def message_list(cls) -> str:
        """Сообщения бота для пользователя Список привычек"""
        return ("✅ - <i>Отметить</i>\n\n"
                "✏️ - <i>Редактировать</i>\n\n"
                "🗑️ - <i>Удалить</i>")

    @classmethod
    def habit_create_name(cls) -> str:
        """Сообщения бота для введения названия привычки"""
        return f"<b>Создание привычки 📝!</b>\n\n<i>Введите название привычки:</i>"

    @classmethod
    def habit_update_name(cls) -> str:
        """Сообщения бота для введения нового названия привычки"""
        return f"<b>Редактирование привычки 📝!</b>\n\n<i>Введите новое название привычки:</i>"

    @classmethod
    def habit_new_name(cls, habit_title) -> str:
        """Сообщения бота для введения нового названия привычки"""
        return f"Редактирование привычки: {habit_title}"

    @classmethod
    def habit_create_frequency(cls) -> str:
        """Сообщения бота для введения частоты привычки"""
        return f"<b>Укажите частоту привычки, например 📝!</b>\n\n<i>два в месяц:</i>"

    @classmethod
    def habit_create_goal_days(cls) -> str:
        """Сообщения бота о формировании привычки"""
        return ("<b>Формирование привычки</b> - это научный процесс!\n\n"
                "🔍 <i>Исследования показывают</i>, что для закрепления нового поведения требуется минимум 21 день!\n\n"
                "📅 <b>Введите количество дней</b> для вашей цели:\n(рекомендуется от 21 до 66 дней)")

    @classmethod
    def habit_adedd(cls) -> str:
        """Сообщения бота о добавлении привычки"""
        return f"🔵Привычка успешно добавлена!"

    @classmethod
    def habit_remind(cls, habit_title) -> str:
        """Сообщения бота об отметки привычки"""
        return f"Привычка '{habit_title}' отмечена!"

    @classmethod
    def habit_finished(cls, habit_title) -> str:
        """Сообщения бота об завершении привычки"""
        return f"🎉 Поздравляем! Привычка '{habit_title}' завершена!"

    @classmethod
    def habit_deleted(cls, habit_title) -> str:
        """Сообщения бота об удалении привычки"""
        return f"Привычка '{habit_title}' удалена!"

    @classmethod
    def habit_done_and_deleted(cls, habit_title) -> str:
        """Сообщения бота об завершении и удалении привычки"""
        return f"🎉 Привычка '{habit_title}' выполнена и удалена!"

    @classmethod
    def habit_congratulations(cls, habit_title) -> str:
        """Сообщения бота об Достижении цели привычки!!!"""
        return ("✨ <b>Поздравляем!</b> ✨\n\n"
                "Вы достигли цели по привычке:\n"
                f"🏅 <b>{habit_title}</b>\n\n"
                "Так держать!"
        )

    @classmethod
    def habit_dont_forget1(cls) -> str:
        """Сообщения бота об не забывать о привычке"""
        return "Не забывайте выполнить привычку!"

    @classmethod
    def habit_dont_forget2(cls,  habit_title) -> str:
        """Сообщения бота об не забывать о привычке"""
        return f"⏰ Напоминаем: не забудьте {habit_title} сегодня!"

    @classmethod
    def habit_updated(cls, hab, new_hab) -> str:
        """Сообщения бота об изменении привычки"""
        return f"🔵Привычка {hab} успешно изменена на {new_hab}!"

    @classmethod
    def habit_exist(cls) -> str:
        """Сообщения бота о том что уже есть привычка"""
        return f"🔴Эта привычка уже существует. Пожалуйста, введите другую."

    @classmethod
    def habit_goal_days_is_digit(cls) -> str:
        """Сообщения бота о том что goal days должно быть числом"""
        return f"🔴Пожалуйста введите числовое значение"

    @classmethod
    def send_habit_details(cls, habit):
        """Сообщение бота - вывод модели привычки"""
        return f"""
    <b>🏷 Привычка:</b> <i>{habit.title}</i>
    <b>🔄 Частота выполнения:</b> {habit.frequency}
    <b>🎯 Цель (количество дней):</b> {habit.goal_days}
    <b>📊 Отслеживания:</b> {"📭 Нет отслеживаний" if not habit.trackings else "\n" + "\n".join(
    f"{'✅' if t.was_performed else '❌'} {t.date.strftime('%d.%m.%Y %H:%M')}" 
    for t in habit.trackings)}
    <b>🆔 ID привычки:</b> <code>{habit.id}</code>
        """

    @classmethod
    def count_remind(cls, remaining) -> str:
        """Сообщения бота о том сколько осталось отметок"""
        return f"Осталось отметок сегодня: {remaining}"

    # ОШИБКИ
    @classmethod
    def try_again_later(cls, exc) -> str:
        """Сообщения бота об ошибке, попробовать позже"""
        return f"Произошла ошибка, попробуйте позже {exc}"

    @classmethod
    def wrong_input(cls, exc) -> str:
        """Сообщения бота об неправильном вводе"""
        return f"Неправильный формат ввода привычки. 🛑 {exc}"

    @classmethod
    def wrong_input2(cls, exc) -> str:
        """Сообщения бота об неправильном вводе"""
        return f"Неправильный формат ввода частоты. 🛑 {exc}"

    @classmethod
    def not_find(cls, exc) -> str:
        """Сообщения бота об отсутствии в базе"""
        return f"Привычка отсутствует в базе {exc}"

    @classmethod
    def habit_limit_error(cls, habit_title, frequency) -> str:
        """Сообщения бота о том что превышен лимит"""
        return f"🚫 Лимит привычки '{habit_title}' исчерпан ({frequency})"

