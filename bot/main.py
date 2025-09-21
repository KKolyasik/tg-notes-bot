import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, RedisEventIsolation
from redis.asyncio import Redis

from bot.core.config import settings
from bot.handlers.notes.create import router as create_note_router
from bot.handlers.start import router as start_router


bot = Bot(
        settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

redis = Redis.from_url(settings.redis_url())

storage = RedisStorage(redis)

dp = Dispatcher(
    storage=storage,
    events_isolation=RedisEventIsolation(redis=redis),
)
dp.include_router(create_note_router)
dp.include_router(start_router)


async def main():

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
