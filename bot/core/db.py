from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from bot.core.config import settings


class Base(DeclarativeBase):
    """Базовый класс для декларативного описания моделей."""


engine = create_async_engine(settings.db_url)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
