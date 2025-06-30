import datetime
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    #Fast API
    FASTAPI_CONFIG: dict = {
        "title": "ChatBotRemember🌞",
        "description": "_Чат бот для трекинга привычек._",
        "version": "1.0.0",
        "contact": {
            "title": "email",
            "name": "Скорик Евгений",
            "email": "3653444@bk.ru"
        },
    }
    #UVICORN
    UVICORN_PORT: int = 8000
    UVICORN_HOST: str = "0.0.0.0"

    # Auth (JWT)
    SECRET_KEY: str = os.getenv('SECRET_JWT_KEY')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: datetime.timedelta = datetime.timedelta(hours=12)

    # Telegram Bot
    KEY: str = os.getenv('TELEGRAM_BOT_API_KEY')

    # PosgresQL Database
    URL: str = os.getenv('POSTGRESQL_DATABASE_URL')

    # SQL Bot Database
    URL_BOT: str = os.getenv('SQL_DATABASE_BOT_URL')

    API_URL: str = "http://api:8000" if os.getenv("IN_DOCKER") else "http://localhost:8000"
    IN_DOCKER: bool = False


settings = Settings()


