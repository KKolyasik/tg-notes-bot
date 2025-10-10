from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage
from fastapi import FastAPI
from redis.asyncio import Redis
import uvicorn

from bot.core.config import settings
from bot.handlers.notes.create import router as create_note_router
from bot.handlers.notes.list import router as list_router
from bot.handlers.start import router as start_router
from bot.webhooks.telegram import router as webhook_router

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = settings.WEBHOOK_SECRET
WEBHOOK_URL = f"{settings.BASE_WEBAPP_URL}{WEBHOOK_PATH}"


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    dp.include_router(list_router)

    app.state.bot = bot
    app.state.dp = dp
    app.state.redis = redis

    url_webhook = f"{settings.BASE_WEBAPP_URL}/webhook"
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=url_webhook,
        secret_token=WEBHOOK_SECRET,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    yield
    await bot.delete_webhook(drop_pending_updates=False)
    await bot.close()
    await redis.close()


app = FastAPI(lifespan=lifespan)
app.include_router(webhook_router, prefix="")


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
