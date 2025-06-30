from typing import Optional, Type

from aiogram.types import ErrorEvent

from app.services.loging import get_logger

logger = get_logger("errors_logger")


class AppError(Exception):
    """Базовая ошибка приложения с автоматической генерацией сообщений"""

    def __init__(
            self,
            tech_message: str,
            user_message: Optional[str] = None,
            exception_type: Optional[Type[Exception]] = None
    ):
        """
        :param tech_message: Техническое сообщение для логов
        :param user_message: Сообщение для пользователя (если None - берётся из exception_type)
        :param exception_type: Тип для isinstance проверок (если отличается от класса)
        """
        self.tech_message = tech_message
        self._user_message = user_message
        self._type = exception_type or self.__class__
        super().__init__(tech_message)

    @property
    def user_message(self) -> str:
        return self._user_message or f"❌ {self.tech_message}"

    def __instancecheck__(self, instance) -> bool:
        return isinstance(instance, self._type)


class NotFoundError(AppError):
    """Когда сущность не найдена в БД"""

    def __init__(self, entity_name: str):
        super().__init__(
            tech_message=f"{entity_name} not found",
            user_message=f"🔍 {entity_name.capitalize()} не найден(а)"
        )


class InvalidInputError(AppError):
    """Некорректные входные данные"""

    def __init__(self, field: str = "", details: str = ""):
        super().__init__(
            tech_message=f"Invalid input: {field} {details}".strip(),
            user_message=f"⚠️ Некорректное значение {field}" if field else "⚠️ Ошибка ввода"
        )


class AccessDeniedError(AppError):
    """Проблемы с авторизацией/правами"""

    def __init__(self):
        super().__init__(
            tech_message="Access denied",
            user_message="🚫 Нет доступа, или Ваш токен устарел, нажмите /start"
        )


class DatabaseError(AppError):
    """Ошибки работы с БД"""

    def __init__(self, details: str = ""):
        super().__init__(
            tech_message=f"Database error: {details}",
            user_message="🔧 Ошибка базы данных"
        )


async def global_bot_error_handler(event: ErrorEvent) -> bool:
    """Централизованная обработка всех ошибок бота"""

    logger.info("Обрабатываем глобальную ошибку")

    error = event.exception

    if isinstance(error, AppError):
        logger.warning(f"Business error: {error.tech_message}", exc_info=error)
    else:
        logger.critical(f"Unhandled error: {str(error)}", exc_info=error)

    user_message = (
        error.user_message if isinstance(error, AppError)
        else "❌ Непредвиденная ошибка. Админ уже уведомлён"
    )

    try:
        update = event.update

        if update.message:
            await update.message.answer(user_message)
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.message.answer(user_message)
    except Exception as e:
        logger.error(f"Failed to send error message: {str(e)}")

    return True
