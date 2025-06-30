# ChatBotRemember
если нужны requirements.txt: 
```
poetry export --format=requirements.txt --output=requirements.txt --without-hashes
```


## 🚀 Запуск проекта

- переименовать .env.example на .env и изменить:
- TELEGRAM_BOT_API_KEY=Ваш АПИ КЛЮЧ - поменять на токен полученный в телеграмме через BotFather
- POSTGRESQL_DATABASE_URL=postgresql+asyncpg://admin:admin@localhost/remember_bot_db - по умолчанию
- SECRET_JWT_KEY=набор рандомных символов - любую JWT комбинацию
- ALEMBIC_MIGRATIONS_PATH=migrations - оставить

### 1. Локально (с Poetry)  
```bash
git clone https://github.com/EvgenySkorik/ChatBotRemember
poetry install
poetry run python app/run.py
```
### 2. В Docker
Создайте .env-файл:

bash
```
cp .env
```
Заполните .env своими ключами:

- TELEGRAM_BOT_API_KEY=ваш_ключ
- POSTGRESQL_DATABASE_URL=postgresql://user:pass@db:5432/db_name
- SECRET_JWT_KEY=ваш_секрет
Запустите:

bash
```
docker-compose up --build
```

⚙️ Настройки
FastAPI: http://localhost:8000/docs

Bot: t.me/ваш_бот

БД: PostgreSQL (порт 5432).