from typing import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from bot.repositories.users import user_crud
from bot.repositories.notes import note_crud
from bot.repositories.reminder import reminder_crud


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

    scheduled_at = data.get("remaind_at")
    if scheduled_at is None:
        await answer(
            "Не удалось получить время напоминания, попробуйте ещё раз",
        )
        return

    note_payload = {
        "title": data.get("title", ""),
        "body": data.get("body", ""),
    }
    note = await note_crud.create_object(note_payload, session, user)

    reminder_payload = {
        "note_id": note.id,
        "scheduled_at": scheduled_at,
        "next_run_at": scheduled_at,
        "chat_id": chat_id,
        "status": "scheduled",
    }
    await reminder_crud.create_object(reminder_payload, session, user)
    await state.clear()
    await answer("Заметка создана")
