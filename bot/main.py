import os

import telebot
from dotenv import load_dotenv
from telebot import types

load_dotenv()

tw_bot = telebot.TeleBot(os.getenv("TG_TOKEN"))


def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Мои сайты", callback_data="sites"),
        types.InlineKeyboardButton("Мой баланс", callback_data="balance"),
        types.InlineKeyboardButton("Мои домены", callback_data="domains"),
    )
    return markup


@tw_bot.message_handler(commands=["start"])
def start(message):
    tw_bot.send_message(
        message.chat.id,
        "Привет! Готов подсказать информацию по твоему аккаунту виртуального хостинга Timeweb.",
        reply_markup=main_menu(),
    )


if __name__ == "__main__":
    tw_bot.infinity_polling()
