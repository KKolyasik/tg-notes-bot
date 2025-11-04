from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.db import SessionFactory
from bot.repositories.users import user_crud
from bot.keyboards.text_kbs import main_kb
from bot.middlewares.db import DbSessionMiddleware

router = Router(name="Стартовый роутер")
router.message.middleware(DbSessionMiddleware(SessionFactory))
router.callback_query.middleware(DbSessionMiddleware(SessionFactory))


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    text = (
        "<b><i><u>🙌 Хэй! Это «Planerka» 📅</u></i></b>\n"
        "Здесь всё по плану: создавай заметки и получай напоминания вовремя 🚀"
    )
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    user = await user_crud.get_user_by_tg_id(user_id, session)
    if not user:
        user = await user_crud.create_object(
            {
                "tg_id": user_id,
                "username": username,
                "chat_id": chat_id,
            },
            session,
        )

    if user.chat_id != chat_id:
        await user_crud.update_obj(user, {"chat_id": chat_id}, session)
    await message.answer(
        text,
        reply_markup=main_kb(),
    )
