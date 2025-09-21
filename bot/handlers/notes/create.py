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
from bot.constants import BTN_CREATE, ISO_REGEX


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
    text = (
        "<b><i><u>✍️ Заголовок заметки</u></i></b>/\n"
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


@router.callback_query(NewNote.body, F.data == "note:skip_body")
async def create_note_withot_body(
    call: CallbackQuery,
    state: FSMContext,
):
    """Хэндлер на создание заметки без тела."""
    await state.update_data(body="")
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
    await state.set_state(NewNote.remaind_at)


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
    await state.set_state(NewNote.remaind_at)


@router.message(F.text.regexp(ISO_REGEX), NewNote.remaind_at)
async def handle_webapp_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(remaind_at=message.text)
    await save_note_from_state(
        state,
        session,
        message.from_user.id,
        message
    )
