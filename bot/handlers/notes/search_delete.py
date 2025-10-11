from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.db import SessionFactory
from bot.middlewares.db import DbSessionMiddleware
from bot.repositories.notes import note_crud
from bot.keyboards.callback import EditNote
from bot.utils.enums import EditNoteAction


router = Router(name="Удаление заметок")
router.message.middleware(DbSessionMiddleware(SessionFactory))
router.callback_query.middleware(DbSessionMiddleware(SessionFactory))


@router.callback_query(EditNote.filter(F.action == EditNoteAction.delete))
async def delete_note(
    callback: CallbackQuery,
    callback_data: EditNote,
    session: AsyncSession,
):
    """Хэндлер на удаление заметки."""
    note = await note_crud.get_object_by_id(callback_data.note_id, session)
    await note_crud.delete_obj(note, session)
    await callback.message.edit_text("Заметка успешно удалена")
    await callback.message.answer("Готово ✅")
