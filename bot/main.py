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


@tw_bot.callback_query_handler(func=lambda call: True)
def on_menu_click(call):
    tw_bot.answer_callback_query(call.id)

    if call.data == "sites":
        text = "Здесь будет список сайтов"
    elif call.data == "domains":
        text = "Здесь будет список доменов"
    elif call.data == "balance":
        text = "Здесь будет баланс"
    else:
        text = "Неизвестное сообщение"

    try:
        tw_bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu(),
        )
    except telebot.apihelper.ApiTelegramException as error:
        if "message is not modified" not in error.description:
            raise


if __name__ == "__main__":
    tw_bot.infinity_polling()
