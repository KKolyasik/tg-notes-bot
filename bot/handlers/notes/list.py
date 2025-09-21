from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession

from bot.constants import BTN_LIST, LIMIT_NOTES
from bot.services.notes import get_user_notes
from bot.keyboards.inline_kbs import get_notes_kb, NotesPaginate


router = Router(name="Список заметок")


@router.message(or_f(Command("list"), F.text == BTN_LIST))
async def get_list_notes(message: Message, session: AsyncSession):
    """Показать первую страницу заметок."""
    offset = 0
    notes, total = await get_user_notes(
        session,
        message,
        limit=LIMIT_NOTES,
        offset=offset,
    )

    text = "Вот ваши заметки\nНажмите для редактирования"
    await message.answer(
        text,
        reply_markup=get_notes_kb(
            notes,
            limit=LIMIT_NOTES,
            offset=offset,
            total=total,
        ),
    )


@router.callback_query(NotesPaginate.filter())
async def paginate_notes(
    cb: CallbackQuery,
    callback_data: NotesPaginate,
    session: AsyncSession,
):
    """Переключение страниц."""
    offset = max(int(callback_data.offset), 0)
    notes, total = await get_user_notes(
        session,
        cb.message,
        limit=LIMIT_NOTES,
        offset=offset,
    )

    await cb.message.edit_reply_markup(
        reply_markup=get_notes_kb(
            notes,
            limit=LIMIT_NOTES,
            offset=offset,
            total=total,
        )
    )
    await cb.answer()
