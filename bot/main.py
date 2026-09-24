import os

import telebot
from dotenv import load_dotenv

load_dotenv()

tw_bot = telebot.TeleBot(os.getenv("TG_TOKEN"))


@tw_bot.message_handler(commands=["start"])
def start(message):
    tw_bot.send_message(
        message.chat.id,
        "Привет! Готов подсказать информацию по твоему аккаунту виртуального хостинга Timeweb.",
    )

if __name__ == "__main__":
    tw_bot.infinity_polling()
