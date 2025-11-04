from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

from bot.core.config import settings


class Base(DeclarativeBase):
    """Базовый класс для декларативного описания моделей."""


engine = create_async_engine(settings.db_url)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    """Функция для DI, которая создает асинхронную сессию SA."""
    async with SessionFactory() as session:
        yield session

DbSession = Annotated[AsyncSession, Depends(get_async_session)]
