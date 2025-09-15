from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings


Base = declarative_base()

engine = create_async_engine(settings.DB_URL)

SessionFactory = async_sessionmaker(engine)
