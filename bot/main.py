import requests
import telebot
from telebot import types

from bot.config import TG_TOKEN
from bot.db import (
    delete_auth_state,
    get_auth_state,
    get_user,
    save_auth_state,
    save_user,
)
from bot.tw_api import TimewebAPIError, get_token

tw_bot = telebot.TeleBot(TG_TOKEN)


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
    telegram_id = message.from_user.id
    user = get_user(telegram_id)

    if user is not None:
        tw_bot.send_message(
            message.chat.id,
            f"С возвращением! Аккаунт: {user.login}",
            reply_markup=main_menu(),
        )
    else:
        save_auth_state(telegram_id, "app_key")
        tw_bot.send_message(
            message.chat.id,
            "Привет! Для начала авторизуйтесь.\nВведите ключ API:",
        )


@tw_bot.message_handler(content_types=["text"])
def on_text(message):
    telegram_id = message.from_user.id
    state = get_auth_state(telegram_id)

    if state is None:
        tw_bot.send_message(message.chat.id, "Нажмите /start, чтобы начать.")
        return

    text = message.text.strip()

    if state.step == "app_key":
        tw_bot.delete_message(message.chat.id, message.message_id)
        save_auth_state(telegram_id, "login", app_key=text)
        tw_bot.send_message(message.chat.id, "Введите логин:")

    elif state.step == "login":
        save_auth_state(telegram_id, "password", login=text, app_key=state.app_key)
        tw_bot.send_message(message.chat.id, "Введите пароль:")

    elif state.step == "password":
        tw_bot.delete_message(message.chat.id, message.message_id)

        try:
            token = get_token(state.login, text, state.app_key)
        except (TimewebAPIError, requests.RequestException):
            save_auth_state(telegram_id, "app_key")
            tw_bot.send_message(
                message.chat.id,
                "Не удалось авторизоваться: проверьте ключ, логин и пароль.\n"
                "Попробуем ещё раз. Введите ключ API:",
            )
            return

        save_user(telegram_id, state.login, state.app_key, token)
        delete_auth_state(telegram_id)
        tw_bot.send_message(
            message.chat.id,
            f"Готово! Вы вошли как {state.login}.",
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
