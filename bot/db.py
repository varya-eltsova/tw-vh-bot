from datetime import datetime

from sqlalchemy import BigInteger, String, create_engine, func
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from bot.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

DATABASE_URL = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_NAME,
    query={"charset": "utf8mb4"},
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "tw_bot_users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    login: Mapped[str] = mapped_column(String(64))
    app_key: Mapped[str] = mapped_column(String(255))
    token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


def save_user(telegram_id, login, app_key, token):
    with Session(engine) as session:
        session.merge(
            User(telegram_id=telegram_id, login=login, app_key=app_key, token=token)
        )
        session.commit()


def get_user(telegram_id):
    with Session(engine) as session:
        return session.get(User, telegram_id)


def delete_user(telegram_id):
    with Session(engine) as session:
        user = session.get(User, telegram_id)
        if user is not None:
            session.delete(user)
            session.commit()
