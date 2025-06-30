import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.add_habit_handlers import add_habit_router
from app.bot.add_list_habits_handlers import list_habits_router
from app.bot.bot_instance import set_bot
from app.bot.bot_main import start_router
from app.bot.exceptions_handlers import global_bot_error_handler
from app.bot.reminder_handlers import reminder_router
from app.bot.trackings_handlers import trackings_router
from app.bot.update_habit_handlers import update_habit_router
from app.conf import settings
from app.services.loging import get_logger
from app.services.scheduler import scheduler
from app.services.security import AuthMiddleware

test_logger = get_logger("setup_test")
test_logger.info("=== ЛОГГЕР УСПЕШНО ИНИЦИАЛИЗИРОВАН ===")
bot = Bot(token=settings.KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML), timeout=30)
dp = Dispatcher(storage=MemoryStorage())


async def run_bot():
    set_bot(bot)
    dp.update.middleware(AuthMiddleware())
    dp.errors.register(global_bot_error_handler)
    dp.include_routers(
        start_router,
        add_habit_router,
        list_habits_router,
        update_habit_router,
        trackings_router,
        reminder_router
    )

    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())