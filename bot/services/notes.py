from typing import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from bot.repositories.users import user_crud
from bot.repositories.notes import note_crud


async def save_note_from_state(
    state: FSMContext,
    session: AsyncSession,
    user_id: int,
    answer: Callable[[str], Awaitable[object]],
):
    """Функция на создание заметки."""
    data = await state.get_data()
    user = await user_crud.get_user_by_tg_id(user_id, session)
    if not user:
        user = await user_crud.create_object(session)
    await note_crud.create_object(data, session, user)
    await state.clear()
    await answer("Заметка сохранена")
