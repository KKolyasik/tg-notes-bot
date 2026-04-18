from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from fastapi import APIRouter, Depends, HTTPException, Response, status

from bot.core.db import DbSession
from bot.repositories.users import user_crud
from bot.api.deps import service_key_required
from bot.services.digest import create_daily_digest
from bot.schemas.digest import DailyDigest
from bot.services.utils import make_bot, format_digest_html
from bot.core.config import settings


router = APIRouter(prefix="/internal/digest", tags=["internal"])


@router.get(
    "/build",
    dependencies=[Depends(service_key_required)],
)
async def build_digest(
    session: DbSession,
) -> DailyDigest:
    return await create_daily_digest(session)


@router.post(
    "/send",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(service_key_required)],
)
async def send_digest(
    session: DbSession,
    payload: DailyDigest,
    bot: Bot = Depends(make_bot),
) -> None:

    text = format_digest_html(digest=payload)
    failed = []

    for user_id in settings.TELEGRAM_ADMIN_IDS:
        chat_id = await user_crud.get_chat_id_by_tg_id(user_id, session)
        if not chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="У админов нет chat_id",
            )
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except TelegramAPIError:
            failed.append(chat_id)
    if failed:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "Не удалось отправить часть сообщений",
                "failed_ids": failed,
            },
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
