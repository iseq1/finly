import os
from dotenv import load_dotenv

load_dotenv()  # Загружает .env


class Config:
    # Общие настройки
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    FLASK_APP = os.getenv("FLASK_APP")
    FLASK_ENV = os.getenv("FLASK_ENV")

    # Telegram Bot
    TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
    TG_BOT_SECRET_KEY = os.getenv("TG_BOT_SECRET_KEY")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
