"""Настройки бота из файла .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Абсолютный путь к корню проекта. На хостинге Apache запускает код из своей
# папки, поэтому относительные пути (".env", "bot.log") не сработают.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

TG_TOKEN = os.getenv("TG_TOKEN")
# Адрес посредника к Telegram API. Нужен там, где api.telegram.org недоступен.
TG_API_URL = os.getenv("TG_API_URL")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

LOG_FILE = BASE_DIR / "bot.log"

# Без этих настроек бот не работает ни локально, ни на хостинге.
# Лучше сразу остановиться с понятной ошибкой, чем упасть позже с непонятной.
REQUIRED = {
    "TG_TOKEN": TG_TOKEN,
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}

missing = [name for name, value in REQUIRED.items() if not value]
if missing:
    raise RuntimeError("В .env не заданы: " + ", ".join(missing))
