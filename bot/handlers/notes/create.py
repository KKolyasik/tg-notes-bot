from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.constants import BTN_CREATE, ISO_REGEX
from bot.core.db import SessionFactory
from bot.keyboards.inline_kbs import get_timesnap, skip_body_note_kb
from bot.middlewares.db import DbSessionMiddleware
from bot.services.notes import save_note_from_state

router = Router(name="Создание заметки")
router.message.middleware(DbSessionMiddleware(SessionFactory))
router.callback_query.middleware(DbSessionMiddleware(SessionFactory))


class NewNote(StatesGroup):
    title: str = State()
    body: str = State()
    remind_at: datetime = State()


@router.message(or_f(Command("new"), F.text == BTN_CREATE))
async def new_note(message: Message, state: FSMContext):
    """Хэндлер на создание новой заметки."""
    text = (
        "<b><i><u>✍️ Заголовок заметки</u></i></b>\n"
        "📝 Введите заголовок для заметки — коротко и ясно!"
    )
    await message.answer(text)
    await state.set_state(NewNote.title)


@router.message(F.text & ~F.text.startswith("/"), NewNote.title)
async def got_title(message: Message, state: FSMContext):
    """Хэндлер на получение заголовка заметки."""
    await state.update_data(title=message.text.strip())
    await state.set_state(NewNote.body)
    text = (
        "<b><i><u>📓 Тело заметки</u></i></b>\n"
        "📄 Теперь можешь добавить подробности"
        "(или пропусти этот шаг, если заметка короткая)"
    )
    await message.answer(
        text,
        reply_markup=skip_body_note_kb(),
    )


@router.callback_query(NewNote.body, F.data == "decline")
async def cancel_note(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer("Отменено")
    await call.message.answer("Окей, создание заметки отменил ✅")


@router.callback_query(NewNote.body, F.data == "note:skip_body")
async def create_note_without_body(
    call: CallbackQuery,
    state: FSMContext,
):
    """Хэндлер на создание заметки без тела."""
    await state.update_data(body=None)
    await call.answer("Далее")
    text = (
        "<b><i><u>📍 Время заметки</u></i></b>\n"
        "⏰ Укажи время, когда напомнить тебе об этой заметке"
    )
    msg = await call.message.answer(text, reply_markup=get_timesnap())
    await state.update_data(
        picker_msg_id=msg.message_id,
        picker_chat_id=msg.chat.id,
    )
    await state.set_state(NewNote.remind_at)


@router.message(F.text & ~F.text.startswith("/"), NewNote.body)
async def got_body(message: Message, state: FSMContext):
    """Хэндлер на создание заметки с телом."""
    await state.update_data(body=message.text.strip())
    text = (
        "<b><i><u>📍 Время заметки</u></i></b>\n"
        "⏰ Укажи время, когда напомнить тебе об этой заметке"
    )
    msg = await message.answer(text, reply_markup=get_timesnap())

    await state.update_data(
        picker_msg_id=msg.message_id,
        picker_chat_id=msg.chat.id,
    )
    await state.set_state(NewNote.remind_at)


@router.message(F.text.regexp(ISO_REGEX), NewNote.remind_at)
async def handle_webapp_data(
    message: Message, state: FSMContext, session: AsyncSession,
):
    await state.update_data(remind_at=message.text)
    await save_note_from_state(
        state,
        session,
        message.from_user.id,
        message,
    )
