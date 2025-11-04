from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.constants import ISO_REGEX
from bot.core.db import SessionFactory
from bot.keyboards.callback import EditNote, NoteOpen
from bot.keyboards.inline_kbs import edit_note_kb, get_timesnap
from bot.middlewares.db import DbSessionMiddleware
from bot.repositories.notes import note_crud
from bot.repositories.reminder import reminder_crud
from bot.services.utils import parse_iso_aware
from bot.utils.enums import EditNoteAction
from bot.utils.text_constructor import get_text_for_edit_note

router = Router(name="Редактирование заметок")
router.message.middleware(DbSessionMiddleware(SessionFactory))
router.callback_query.middleware(DbSessionMiddleware(SessionFactory))


class StateEditNote(StatesGroup):
    title: str = State()
    body: str = State()
    remind_at: datetime = State()


@router.callback_query(NoteOpen.filter())
async def get_user_note(
    callback: CallbackQuery,
    callback_data: NoteOpen,
    session: AsyncSession,
):
    note = await note_crud.get_object_by_id(callback_data.note_id, session)
    text = get_text_for_edit_note(note)
    await callback.message.edit_text(text, reply_markup=edit_note_kb(note))
    await callback.answer()


@router.callback_query(EditNote.filter(F.action == EditNoteAction.header))
async def edit_note_title(
    callback: CallbackQuery,
    callback_data: EditNote,
    state: FSMContext,
):
    """Хэндлер на редактирование заголовка."""
    await state.update_data(
        note_id=callback_data.note_id,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await state.set_state(StateEditNote.title)
    await callback.message.edit_text(
        "Введите новый текст заголовка",
        reply_markup=None,
    )
    await callback.answer()


@router.message(F.text & ~F.text.startswith("/"), StateEditNote.title)
async def got_title(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
):
    data = await state.get_data()
    note_id = data.get("note_id")
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")
    if note_id is None:
        await bot.edit_message_text(
            text="Не нашёл идентификатор заметки. Начните заново.",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )
        await state.clear()
        return

    new_title = message.text.strip()
    if not new_title:
        await bot.edit_message_text(
            text="Заголовок не может быть пустым. Введите ещё раз:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )
        return

    note = await note_crud.get_object_by_id(note_id, session)
    await note_crud.update_obj(note, {"title": new_title}, session)

    await bot.edit_message_text(
        text="✅ Заголовок обновлён.",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None,
    )

    await state.clear()


@router.callback_query(EditNote.filter(F.action == EditNoteAction.body))
async def edit_note_body(
    callback: CallbackQuery,
    callback_data: EditNote,
    state: FSMContext,
):
    """Хэндлер на редактирование тела запроса."""
    await state.update_data(
        note_id=callback_data.note_id,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await state.set_state(StateEditNote.body)
    await callback.message.edit_text(
        "Введите новый текст заметки",
        reply_markup=None,
    )
    await callback.answer()


@router.message(F.text & ~F.text.startswith("/"), StateEditNote.body)
async def got_body(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
):
    data = await state.get_data()
    note_id = data.get("note_id")
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")
    if note_id is None:
        await bot.edit_message_text(
            text="Не нашёл идентификатор заметки. Начните заново.",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )
        await state.clear()
        return

    new_body = message.text.strip()
    if not new_body:
        await bot.edit_message_text(
            text="Тело заметки не может быть пустым. Введите ещё раз:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )
        return

    note = await note_crud.get_object_by_id(note_id, session)
    await note_crud.update_obj(note, {"body": new_body}, session)

    await bot.edit_message_text(
        text="✅ Тело заметки обновлено.",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None,
    )

    await state.clear()


@router.callback_query(EditNote.filter(F.action == EditNoteAction.remind_at))
async def edit_note_remind_at(
    callback: CallbackQuery,
    callback_data: EditNote,
    state: FSMContext,
):
    """Хэндлер на редактирование времени отправки"""
    await state.update_data(
        note_id=callback_data.note_id,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await state.set_state(StateEditNote.remind_at)
    await callback.message.edit_text(
        "Выберете новое время отправки",
        reply_markup=get_timesnap(),
    )
    await callback.answer()


@router.message(F.text.regexp(ISO_REGEX), StateEditNote.remind_at)
async def got_remind_at(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
):
    data = await state.get_data()
    note_id = data.get("note_id")
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")
    if note_id is None:
        await bot.edit_message_text(
            text="Не нашёл идентификатор заметки. Начните заново.",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )
        await state.clear()
        return

    note = await note_crud.get_object_by_id(note_id, session)
    reminder = note.reminder
    celery_task_id = reminder.celery_task_id
    if celery_task_id:
        await bot.edit_message_text(
            text="Уже нельзя перепланировать напоминание",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )
        await state.clear()
        return
    remind_at = parse_iso_aware(message.text)

    await reminder_crud.update_obj(
        reminder,
        {"scheduled_at": remind_at},
        session,
    )

    await bot.edit_message_text(
        text="✅ Время отправки заметки обновлено.",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None,
    )

    await state.clear()


@router.callback_query(EditNote.filter(F.action == EditNoteAction.decline))
async def decline_edit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer()
