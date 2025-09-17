from typing import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from bot.repositories.users import user_crud
from bot.repositories.notes import note_crud
from bot.repositories.reminder import reminder_crud
from bot.services.utils import parse_iso_aware


async def save_note_from_state(
    state: FSMContext,
    session: AsyncSession,
    user_id: int,
    chat_id: int,
    answer: Callable[[str], Awaitable[object]],
):
    """Функция на создание заметки."""
    data = await state.get_data()

    user = await user_crud.get_user_by_tg_id(user_id, session)
    if not user:
        user = await user_crud.create_object({"tg_id": user_id}, session)

    scheduled_at = parse_iso_aware(data.get("remaind_at"))

    note_payload = {
        "title": data.get("title", ""),
        "body": data.get("body", ""),
    }
    note = await note_crud.create_object(note_payload, session)

    reminder_payload = {
        "note_id": note.id,
        "scheduled_at": scheduled_at,
        "chat_id": chat_id,
        "status": "scheduled",
    }
    await reminder_crud.create_object(reminder_payload, session, user)
    await state.clear()
    await answer("Заметка создана")
