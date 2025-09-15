from typing import AsyncGenerator

from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from app.core.config import settings


Base = declarative_base()

engine = create_async_engine(settings.DB_URL)

SessionFabric = async_sessionmaker(engine)


async def get_async_session() -> AsyncGenerator[AsyncSession | None]:
    async with SessionFabric() as session:
        yield session
