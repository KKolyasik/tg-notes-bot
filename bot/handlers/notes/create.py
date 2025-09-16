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
    await call.message.answer("Теперь время", reply_markup=get_timesnap())
    await state.set_state(NewNote.remaind_at)


@router.message(F.text & ~F.text.startswith("/"), NewNote.body)
async def got_body(message: Message, state: FSMContext):
    """Хэндлер на создание заметки с телом."""
    await state.update_data(body=message.text.strip())
    await message.answer("Теперь время", reply_markup=get_timesnap())
    await state.set_state(NewNote.remaind_at)


@router.callback_query(NewNote.remaind_at, F.data == "timesnap")
async def get_time_to_remind(call: CallbackQuery, state: FSMContext):
    pass


@router.message(F.web_app_data)
async def handle_webapp_data(message: Message, state: FSMContext):
    try:
        data: dict = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer("Не удалось получить время")
        return

    iso = data.get("iso_utc")
    if not iso:
        await message.answer("В payload нет iso_utc")
        return
    pass
