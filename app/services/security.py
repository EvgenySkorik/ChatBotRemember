from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from aiogram import BaseMiddleware, types
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import encode, decode, PyJWTError
from pydantic import ValidationError

from app.bot.exceptions_handlers import AppError, DatabaseError, InvalidInputError, AccessDeniedError
from app.conf import settings
from app.services.loging import get_logger

logger = get_logger("security_logger")
security_scheme = HTTPBearer()

class AuthService:
    @staticmethod
    def create_access_token(
            data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Генерация JWT-токена.
        """
        if not isinstance(data, dict) or "sub" not in data:
            raise InvalidInputError("Данные токена", "должны содержать 'sub'")
        try:
            expires_delta = expires_delta or settings.ACCESS_TOKEN_EXPIRE_HOURS
            to_encode = deepcopy(data)
            expire = datetime.now(timezone.utc) + expires_delta
            to_encode.update({"exp": expire, "sub": str(to_encode["sub"])})

            return encode(
                to_encode,
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )
        except Exception as e:
            logger.error(f"Ошибка генерации токена: {e}")
            raise DatabaseError("Не удалось создать токен")

    @staticmethod
    async def verify_token_fastapi(
            credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
    ) -> int:
        """Для FastAPI."""
        try:
            return await AuthService.verify_token(credentials.credentials)
        except AppError as e:
            raise HTTPException(status_code=401, detail=e.user_message)


    @staticmethod
    async def verify_token(token: str) -> int:
        """
        Проверка токена. Возвращает ID пользователя (sub).

        :param token: JWT-токен.
        :return: ID пользователя (str).
        :raises PermissionError: Если токен невалиден.
        """

        if not token:
            raise InvalidInputError("Токен не предоставлен")

        try:
            payload = decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            if (sub := payload.get("sub")) is None:
                raise AccessDeniedError()
            return int(sub)
        except PyJWTError:
            raise AccessDeniedError()
        except (ValidationError, ValueError, TypeError) as e:
            raise InvalidInputError("Некорректный формат токена")
        except Exception as e:
            raise DatabaseError(f"Ошибка проверки токена: {str(e)}")

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Update, data: dict):
        message = None
        if event.message:
            message = event.message
        elif event.callback_query and event.callback_query.message:
            message = event.callback_query.message

        if not message:
            return await handler(event, data)

        if message.text and message.text.startswith(('/start', '/help')):
            return await handler(event, data)

        state = data.get("state")
        if not state:
            await message.answer("🚫 Сессия не найдена. Нажмите /start")
            return None

        user_data = await state.get_data()
        token = user_data.get("token")

        if not token:
            await message.answer("🔒 Требуется авторизация! Нажмите /start")
            return None


        try:
            user_id = await AuthService.verify_token(token)
            data["user_id"] = user_id
            logger.info(f"Токен подтвержден - {token}")
            return await handler(event, data)
        except AppError as e:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка проверки токена: {str(e)}")