
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

engine = None
SessionFactory: async_sessionmaker[AsyncSession] | None = None


async def init_async_db(db_url: str | URL) -> None:
    """Вызываем один раз ПОСЛЕ старта фонового loop (run_coro)."""
    global engine, SessionFactory

    if engine is None:
        engine = create_async_engine(db_url)
        SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def dispose_async_db() -> None:
    global engine, SessionFactory

    if engine is not None:
        await engine.dispose()
        engine = None
        SessionFactory = None


def get_async_session() -> AsyncSession:
    if SessionFactory is None:
        raise RuntimeError("Async DB is not initialized")
    return SessionFactory()
