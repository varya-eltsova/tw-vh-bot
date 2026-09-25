"""Telegram-бот: авторизация, меню и обработка кнопок.

Локально запускается через polling: python -m bot.main
На хостинге тот же бот работает через webhook (см. bot/webhook.py).
"""

import logging

import requests
import telebot
from telebot import types

from bot.config import LOG_FILE, TG_API_URL, TG_TOKEN
from bot.db import (
    delete_auth_state,
    delete_user,
    get_auth_state,
    get_user,
    save_auth_state,
    save_user,
)
from bot.tw_api import TimewebAPIError, get_balance, get_domains, get_sites, get_token

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

if TG_API_URL:
    # С хостинга api.telegram.org недоступен, поэтому все запросы бота
    # к Telegram идут через посредника (deploy/relay-worker.js)
    telebot.apihelper.API_URL = TG_API_URL.rstrip("/") + "/bot{0}/{1}"

# threaded=False: сообщение обрабатывается прямо внутри запроса webhook
tw_bot = telebot.TeleBot(TG_TOKEN, threaded=False)


def main_menu():
    """Кнопки главного меню."""
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Мои сайты", callback_data="sites"),
        types.InlineKeyboardButton("Мой баланс", callback_data="balance"),
        types.InlineKeyboardButton("Мои домены", callback_data="domains"),
    )
    markup.row(
        types.InlineKeyboardButton("Сменить аккаунт", callback_data="change_account"),
    )
    return markup


def format_balance(data):
    """Текст с балансом для пользователя."""
    return f"Баланс: {data['balance']:.2f} {data['currency']}"


def format_domains(data):
    """Текст со списком доменов для пользователя."""
    if not data:
        return "Доменов на аккаунте нет."
    lines = ["Домены на аккаунте:"]
    for domain in data:
        # Кириллические домены приходят в Punycode (xn--...), переводим в обычный вид
        domain = domain.encode().decode("idna")
        lines.append(domain)
    return "\n".join(lines)


def format_sites(data):
    """Текст со списком сайтов для пользователя."""
    if not data:
        return "Сайтов на аккаунте нет."
    lines = ["Ваши сайты:"]
    for site in data:
        lines.append(site["directory"])
    return "\n".join(lines)


@tw_bot.message_handler(commands=["start"])
def start(message):
    """Команда /start: меню для авторизованных, иначе начало авторизации."""
    telegram_id = message.from_user.id
    user = get_user(telegram_id)

    if user is not None:
        tw_bot.send_message(
            message.chat.id,
            f"С возвращением! Аккаунт: {user.login}",
            reply_markup=main_menu(),
        )
    else:
        # Авторизация. Если пользователь нажал /start посреди неё,
        # состояние перезапишется и всё начнётся сначала.
        save_auth_state(telegram_id, "app_key")
        tw_bot.send_message(
            message.chat.id,
            "Привет! Для начала авторизуйтесь.\nВведите ключ API:",
        )


# Обработчик любого текста объявлен после /start: telebot проверяет обработчики
# по порядку, и иначе этот перехватывал бы и саму команду /start.
@tw_bot.message_handler(content_types=["text"])
def on_text(message):
    """Шаги авторизации: ключ API -> логин -> пароль."""
    telegram_id = message.from_user.id
    state = get_auth_state(telegram_id)

    if state is None:
        tw_bot.send_message(message.chat.id, "Нажмите /start, чтобы начать.")
        return

    text = message.text.strip()

    if state.step == "app_key":
        # Ключ и пароль не должны оставаться в переписке
        tw_bot.delete_message(message.chat.id, message.message_id)
        save_auth_state(telegram_id, "login", app_key=text)
        tw_bot.send_message(message.chat.id, "Введите логин:")

    elif state.step == "login":
        # app_key передаём заново, иначе merge затрёт его значением None
        save_auth_state(telegram_id, "password", login=text, app_key=state.app_key)
        tw_bot.send_message(message.chat.id, "Введите пароль:")

    elif state.step == "password":
        tw_bot.delete_message(message.chat.id, message.message_id)

        try:
            token = get_token(state.login, text, state.app_key)
        except (TimewebAPIError, requests.RequestException) as error:
            logger.warning(
                "Неудачная авторизация: telegram_id=%s, login=%s, ошибка: %s",
                telegram_id,
                state.login,
                error,
            )
            save_auth_state(telegram_id, "app_key")
            tw_bot.send_message(
                message.chat.id,
                "Не удалось авторизоваться: проверьте ключ, логин и пароль.\n"
                "Попробуйте ещё раз. Введите ключ API:",
            )
            return

        save_user(telegram_id, state.login, state.app_key, token)
        delete_auth_state(telegram_id)
        logger.info(
            "Пользователь авторизовался: telegram_id=%s, login=%s",
            telegram_id,
            state.login,
        )
        tw_bot.send_message(
            message.chat.id,
            f"Готово! Вы вошли как {state.login}.",
            reply_markup=main_menu(),
        )


@tw_bot.callback_query_handler(func=lambda call: True)
def on_menu_click(call):
    """Нажатия кнопок меню. Результат показывается в том же сообщении."""
    tw_bot.answer_callback_query(call.id)
    user = get_user(call.from_user.id)
    # Кнопку можно нажать в старом сообщении, уже после выхода из аккаунта
    if user is None:
        tw_bot.edit_message_text(
            "Необходима авторизация через /start.",
            call.message.chat.id,
            call.message.message_id,
        )
        return

    if call.data == "change_account":
        delete_user(user.telegram_id)
        logger.info(
            "Пользователь вышел: telegram_id=%s, login=%s",
            user.telegram_id,
            user.login,
        )
        tw_bot.edit_message_text(
            "Вы вышли из аккаунта. Чтобы войти в другой, нажмите /start.",
            call.message.chat.id,
            call.message.message_id,
        )
        return

    try:
        if call.data == "sites":
            text = format_sites(get_sites(user.login, user.app_key, user.token))
        elif call.data == "domains":
            text = format_domains(get_domains(user.login, user.app_key, user.token))
        elif call.data == "balance":
            text = format_balance(get_balance(user.login, user.app_key, user.token))
        else:
            text = "Неизвестная команда!"
    except (TimewebAPIError, requests.RequestException):
        logger.exception(
            "Ошибка API: действие=%s, telegram_id=%s, login=%s",
            call.data,
            user.telegram_id,
            user.login,
        )
        text = "Не удалось получить данные. Попробуйте позже."

    try:
        tw_bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu(),
        )
    except telebot.apihelper.ApiTelegramException as error:
        # При повторном нажатии той же кнопки текст не меняется, и Telegram
        # отвечает этой ошибкой. Сообщение и так актуально, её можно пропустить.
        if "message is not modified" not in error.description:
            raise


if __name__ == "__main__":
    logger.info("Бот запущен в режиме polling")
    tw_bot.infinity_polling()
