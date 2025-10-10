from typing import TYPE_CHECKING

from aiogram.types import Update
from fastapi import APIRouter, Header, HTTPException, Request

from bot.core.config import settings

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher

router = APIRouter()


@router.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None),
) -> dict:
    """Ручка для веб хука."""
    if x_telegram_bot_api_secret_token != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Bad secret")

    bot: Bot = request.app.state.bot
    dp: Dispatcher = request.app.state.dp

    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}
