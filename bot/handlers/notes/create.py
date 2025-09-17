from datetime import datetime
import json

from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.db import SessionFactory
from bot.middlewares.db import DbSessionMiddleware
from bot.keyboards.inline_kbs import skip_body_note_kb, get_timesnap
from bot.handlers.notes.validators import correct_time
from bot.services.notes import save_note_from_state
from bot.constants import BTN_CREATE


router = Router(name="Создание заметки")
router.message.middleware(DbSessionMiddleware(SessionFactory))
router.callback_query.middleware(DbSessionMiddleware(SessionFactory))


class NewNote(StatesGroup):
    title = State()
    body = State()
    remaind_at = State()


@router.message(or_f(Command("new"), F.text == BTN_CREATE))
async def new_note(message: Message, state: FSMContext):
    """Хэндлер на создание новой заметки."""
    await message.answer("Введите заголовок заметки")
    await state.set_state(NewNote.title)


@router.message(F.text & ~F.text.startswith("/"), NewNote.title)
async def got_title(message: Message, state: FSMContext):
    """Хэндлер на получение заголовка заметки."""
    await state.update_data(title=message.text.strip())
    await state.set_state(NewNote.body)
    await message.answer(
        "Теперь текст заметки",
        reply_markup=skip_body_note_kb(),
    )


@router.callback_query(NewNote.body, F.data == "note:skip_body")
async def create_note_withot_body(
    call: CallbackQuery,
    state: FSMContext,
):
    """Хэндлер на создание заметки без тела."""
    await state.update_data(body="")
    await call.answer("Далее")
    await call.message.answer("Теперь время", reply_markup=get_timesnap())
    await state.set_state(NewNote.remaind_at)


@router.message(F.text & ~F.text.startswith("/"), NewNote.body)
async def got_body(message: Message, state: FSMContext):
    """Хэндлер на создание заметки с телом."""
    await state.update_data(body=message.text.strip())
    await message.answer("Теперь время", reply_markup=get_timesnap())
    await state.set_state(NewNote.remaind_at)


@router.message(NewNote.remaind_at)
async def handle_webapp_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    if not message.web_app_data:
        await message.answer("Не удалось получить данные из мини-приложения")
        return

    try:
        payload: dict = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer("Не удалось прочитать данные из виджета 😕")
        return

    iso_utc = payload.get("iso_utc")
    if not iso_utc:
        await message.answer("В полученных данных нет времени")
        return

    try:
        notification_utc = datetime.fromisoformat(
            iso_utc.replace("Z", "+00:00"),
        )
    except ValueError:
        await message.answer("Не удалось прочитать данные из виджета 😕")
        return

    if not correct_time(notification_utc):
        await message.answer("Нельзя ставить напоминмание в прошлое")
        return

    await state.update_data(remaind_at=notification_utc)

    await save_note_from_state(
        state,
        session,
        message.from_user.id,
        message.chat.id,
        message.answer,
    )
