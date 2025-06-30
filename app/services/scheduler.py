import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.bot.bot_instance import get_bot
from app.bot.keyboards import InlineKeyboardRep
from app.services.loging import get_logger

scheduler = AsyncIOScheduler()
logger = get_logger("scheduler_logger")


def generate_cron(frequency: str) -> dict:
    """Генерирует cron-расписание на основе частоты"""
    count_str, period = frequency.split(" в ")
    count = {"один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5}.get(count_str, 1)

    if period == "день":
        # Для "N в день" - случайные часы в интервале 9-21
        return {
            "hour": ",".join(str(h) for h in sorted(random.sample(range(9, 22), count))),
            "minute": "0"
        }

    elif period == "неделю":
        # Для "N в неделю" - случайные дни недели (0-6, где 0=понедельник)
        return {
            "day_of_week": ",".join(map(str, sorted(random.sample(range(7), count)))),
            "hour": "9",
            "minute": "0"
        }

    elif period == "месяц":
        # Для "N в месяц" - случайные дни месяца (1-28)
        return {
            "day": ",".join(str(d) for d in sorted(random.sample(range(1, 29), count))),
            "hour": "9",
            "minute": "0"
        }

    elif period == "квартал":
        # Для "N в квартал" - случайные месяцы из каждого квартала
        quarters = [
            [1, 2, 3],  # 1 квартал
            [4, 5, 6],  # 2 квартал
            [7, 8, 9],  # 3 квартал
            [10, 11, 12]  # 4 квартал
        ]
        months = []
        for q in quarters:
            if count >= len(q):
                months.extend(q)
            else:
                months.extend(random.sample(q, count))
        return {
            "month": ",".join(str(m) for m in sorted(months[:count * 3])),
            "day": "1",
            "hour": "9",
            "minute": "0"
        }

    elif period == "год":
        # Для "N в год" - случайные месяцы года
        return {
            "month": ",".join(str(m) for m in sorted(random.sample(range(1, 13), count))),
            "day": "1",
            "hour": "9",
            "minute": "0"
        }

    else:
        raise ValueError(f"Неизвестный период: {period}")

async def schedule_habit(habit_id: int, chat_id: int, habit_title: str, frequency: str):
    """Добавляет напоминание для привычки."""
    cron = generate_cron(frequency)
    # manual_cron = {
    #     'second': '*/30',  # Каждую минуту
    #     'hour': '*'  # Любой час
    # }
    scheduler.add_job(
        send_reminder,
        "cron",
        args=[chat_id, habit_title],
        id=f"habit_{habit_id}",
        # **manual_cron
        **cron
    )
    logger.info(f"Добавлена задача habit_{habit_id} с параметрами: {cron}")

async def remove_habit_reminder(habit_id: int):
    """Удаляет напоминание привычки."""
    scheduler.remove_job(f"habit_{habit_id}")

async def send_reminder(chat_id: int, habit_title: str):
    """Отправляет уведомление."""
    bot = get_bot()
    if bot:
        keyboard = InlineKeyboardRep.reminder_keyboard(habit_title)
        await bot.send_message(chat_id, f"⏰ Напоминаем о привычке:\n\nВы уже сегодня {habit_title}?", reply_markup=keyboard)
        logger.info("Уведомление отправлено")





