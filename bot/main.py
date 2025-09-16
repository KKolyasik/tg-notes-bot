import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, RedisEventIsolation
from redis.asyncio import Redis

from bot.core.config import settings
from bot.handlers.notes.create import router as create_note_router
from bot.handlers.start import router as start_router
from bot.keyboards.menu import set_commands


async def main():
    bot = Bot(settings.BOT_TOKEN)

    redis = Redis.from_url(settings.redis_url)

    storage = RedisStorage(redis)

    dp = Dispatcher(
        storage=storage,
        events_isolation=RedisEventIsolation(redis=redis),
    )
    dp.include_router(create_note_router)
    dp.include_router(start_router)

    await set_commands(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
