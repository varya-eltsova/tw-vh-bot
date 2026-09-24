import logging

from flask import Flask, abort, request
from telebot.types import Update

from bot.config import WEBHOOK_SECRET
from bot.main import tw_bot

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.post("/webhook")
def webhook():
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not WEBHOOK_SECRET or secret != WEBHOOK_SECRET:
        abort(403)

    update = Update.de_json(request.get_data(as_text=True))
    try:
        tw_bot.process_new_updates([update])
    except Exception:
        logger.exception("Ошибка при обработке обновления %s", update.update_id)
    return ""
