from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from bot.core.config import settings


Base = declarative_base()

engine = create_async_engine(settings.db_url)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
