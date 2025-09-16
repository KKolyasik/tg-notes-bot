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
        user = await user_crud.create_object(session)
    scheduled_at = data.pop("remaind_at")
    note = await note_crud.create_object(data, session, user)
    data["note_id"] = note.id
    data["scheduled_at"] = scheduled_at
    data["next_run_at"] = scheduled_at
    data["chat_id"] = chat_id
    data["status"] = "scheduled"
    data.pop("body")
    data.pop("titile")
    await reminder_crud.create_object(data, session, user)
    await state.clear()
    await answer("Заметка создана")
