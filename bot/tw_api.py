"""Запросы к публичному API Timeweb для виртуального хостинга."""

from typing import Any

import requests

BASE_URL = "https://api.timeweb.ru"
# Без таймаута запрос может зависнуть, а вместе с ним и бот
TIMEOUT = 10


class TimewebAPIError(Exception):
    """API Timeweb вернул ошибку."""


def _check(response: requests.Response) -> None:
    """Выбросить TimewebAPIError, если API ответил ошибкой.

    Без этой проверки при ошибке API (например, неверный пароль)
    код падал бы дальше с непонятным KeyError.
    """
    if response.status_code != 200:
        raise TimewebAPIError(f"{response.status_code}: {response.text}")


def get_token(login: str, password: str, app_key: str) -> str:
    """Получить токен по логину, паролю и ключу API. Токен бессрочный."""
    response = requests.post(
        f"{BASE_URL}/v1.2/access",
        auth=(login, password),
        headers={"x-app-key": app_key},
        timeout=TIMEOUT,
    )
    _check(response)
    return response.json()["token"]


def _get(path: str, app_key: str, token: str) -> Any:
    """Общий GET-запрос с авторизацией (ключ API + токен)."""
    response = requests.get(
        f"{BASE_URL}{path}",
        headers={"x-app-key": app_key, "Authorization": f"Bearer {token}"},
        timeout=TIMEOUT,
    )
    _check(response)
    return response.json()


def get_balance(login: str, app_key: str, token: str) -> dict:
    """Баланс аккаунта: словарь с полями balance, currency и др."""
    return _get(f"/v1.1/finances/accounts/{login}", app_key, token)


def get_sites(login: str, app_key: str, token: str) -> list[dict]:
    """Список сайтов на аккаунте (список словарей)."""
    return _get(f"/v1.1/sites/{login}", app_key, token)


def get_domains(login: str, app_key: str, token: str) -> list[str]:
    """Список доменов на аккаунте (список строк, кириллица в Punycode).

    Метода нет в документации, адрес найден перебором версий API.
    """
    return _get(f"/v1/accounts/{login}/domains", app_key, token)
