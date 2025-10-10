from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.constants import BTN_LIST, LIMIT_NOTES
from bot.core.db import SessionFactory
from bot.keyboards.callback import NotesPaginate
from bot.keyboards.inline_kbs import get_notes_kb
from bot.middlewares.db import DbSessionMiddleware
from bot.services.notes import get_user_notes

router = Router(name="Список заметок")
router.message.middleware(DbSessionMiddleware(SessionFactory))
router.callback_query.middleware(DbSessionMiddleware(SessionFactory))


@router.message(or_f(Command("list"), F.text == BTN_LIST))
async def get_list_notes(message: Message, session: AsyncSession):
    """Показать первую страницу заметок."""
    offset = 0
    notes, total = await get_user_notes(
        session,
        message.from_user.id,
        limit=LIMIT_NOTES,
        offset=offset,
    )

    text = "Вот ваши заметки\nНажмите для редактирования"
    await message.answer(
        text,
        reply_markup=get_notes_kb(
            notes=notes,
            limit=LIMIT_NOTES,
            offset=offset,
            total=total,
        ),
    )


@router.callback_query(NotesPaginate.filter())
async def paginate_notes(
    callback: CallbackQuery,
    callback_data: NotesPaginate,
    session: AsyncSession,
):
    """Переключение страниц."""
    offset = max(int(callback_data.offset), 0)
    notes, total = await get_user_notes(
        session,
        callback.from_user.id,
        limit=LIMIT_NOTES,
        offset=offset,
    )

    await callback.message.edit_reply_markup(
        reply_markup=get_notes_kb(
            notes=notes,
            limit=LIMIT_NOTES,
            offset=offset,
            total=total,
        ),
    )
    await callback.answer()
