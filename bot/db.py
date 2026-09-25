"""Работа с базой данных MySQL: модели и функции для пользователей."""

from datetime import datetime

from sqlalchemy import BigInteger, String, create_engine, func
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from bot.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

# URL.create правильно экранирует спецсимволы в пароле (@, /, :),
# чего не сделала бы обычная f-строка
DATABASE_URL = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_NAME,
    query={"charset": "utf8mb4"},
)

# pool_pre_ping: MySQL сам закрывает долго простаивающие соединения,
# поэтому перед запросом проверяем, что соединение есть
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    """Авторизованный пользователь. Пароль не хранится."""

    __tablename__ = "tw_bot_users"

    # ID пользователя в Telegram. BigInteger, так как ID не помещаются в INT
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    login: Mapped[str] = mapped_column(String(64))
    app_key: Mapped[str] = mapped_column(String(255))
    token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AuthState(Base):
    """На каком шаге авторизации пользователь и что он уже ввёл.

    Хранится в базе, а не в памяти: на хостинге каждое сообщение может
    обрабатываться новым процессом, и память между ними не сохраняется.
    """

    __tablename__ = "tw_bot_auth_states"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    step: Mapped[str] = mapped_column(String(16))  # "app_key", "login", "password"
    login: Mapped[str | None] = mapped_column(String(64))
    app_key: Mapped[str | None] = mapped_column(String(255))


def save_user(telegram_id, login, app_key, token):
    """Сохранить пользователя после успешной авторизации."""
    with Session(engine) as session:
        # merge добавляет запись или обновляет существующую:
        # при повторной авторизации данные просто перезапишутся
        session.merge(
            User(telegram_id=telegram_id, login=login, app_key=app_key, token=token)
        )
        session.commit()


def get_user(telegram_id):
    """Найти пользователя по Telegram ID. None, если он не авторизован."""
    with Session(engine) as session:
        return session.get(User, telegram_id)


def delete_user(telegram_id):
    """Удалить пользователя (выход из аккаунта)."""
    with Session(engine) as session:
        user = session.get(User, telegram_id)
        if user is not None:
            session.delete(user)
            session.commit()


def save_auth_state(telegram_id, step, login=None, app_key=None):
    """Запомнить шаг авторизации и уже введённые данные."""
    # merge перезаписывает запись целиком, поэтому уже введённые
    # login и app_key нужно передавать заново на каждом шаге
    with Session(engine) as session:
        session.merge(
            AuthState(telegram_id=telegram_id, step=step, login=login, app_key=app_key)
        )
        session.commit()


def get_auth_state(telegram_id):
    """Узнать, на каком шаге авторизации пользователь. None - не авторизуется."""
    with Session(engine) as session:
        return session.get(AuthState, telegram_id)


def delete_auth_state(telegram_id):
    """Удалить состояние после завершения авторизации."""
    with Session(engine) as session:
        state = session.get(AuthState, telegram_id)
        if state is not None:
            session.delete(state)
            session.commit()


def init_db():
    """Создать таблицы, которых ещё нет. Существующие не меняются."""
    Base.metadata.create_all(engine)


# Создание таблиц: python -m bot.db
if __name__ == "__main__":
    init_db()
