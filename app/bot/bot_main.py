from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.repository import UserRep
from app.api.router import registration_user
from app.bot.exceptions_handlers import NotFoundError
from app.bot.keyboards import ReplyKeyboardRep
from app.bot.messages import MU
from app.conf import settings
from app.models.shemas import RegistrationUserShema
from app.services.loging import get_logger
from app.services.security import AuthService
from app.bot.states import CommonState

logger = get_logger("bot_loger")
start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message, state: FSMContext):
    """Запуск стартового меню бота /start
    Регистрация в БД, Получение токена JWT"""

    user_shema = RegistrationUserShema(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username
    )
    await registration_user(user_shema)

    access_token = AuthService.create_access_token(
        data={"sub": message.from_user.id},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_HOURS
    )
    await message.reply(
        MU.token(access_token),
        parse_mode="HTML"
    )
    await state.update_data(token=access_token)
    await state.set_state(CommonState.token)
    logger.info(f"TOKEN {access_token} {message.from_user.id}")

    await message.answer(
        MU.start_message(message),
        reply_markup=ReplyKeyboardRep.start_keyboard(),
        parse_mode=MU.HTML
    )
    await message.answer_dice(emoji="⚽️")

    logger.info(
        f"Пользователь подключился: {message.from_user.username} "
        f"ID-{str(message.from_user.id)} к RememberBot"
    )


@start_router.message(F.text == '**')
async def cmd_start_3(message: Message):
    await message.answer('Запуск скрипта TEST')

    logger.info("Тестовое сообщение в лог")
    logger.warning("Тестовое предупреждение")
    logger.error("Тест ошибки")
    raise NotFoundError("тестовый пользователь")

