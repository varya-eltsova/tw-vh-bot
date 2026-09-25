"""Flask-приложение для приёма обновлений от Telegram на хостинге."""

import logging

from flask import Flask, abort, request
from telebot.types import Update

from bot.config import WEBHOOK_SECRET
from bot.main import tw_bot

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.post("/webhook")
def webhook():
    """Принять обновление от Telegram и передать его боту."""
    # Проверяем секрет от Telegram, иначе кто угодно сможет слать боту
    # поддельные сообщения. Если секрет не настроен, отклоняем всё.
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not WEBHOOK_SECRET or secret != WEBHOOK_SECRET:
        abort(403)

    update = Update.de_json(request.get_data(as_text=True))
    try:
        tw_bot.process_new_updates([update])
    except Exception:
        # Записываем ошибку в лог, но Telegram отвечаем «ок»,
        # иначе он будет повторно присылать то же сообщение
        logger.exception("Ошибка при обработке обновления %s", update.update_id)
    return ""
