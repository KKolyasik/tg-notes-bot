from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.constants import LIMIT_NOTES, IMG_DIR
from bot.models import Note, Reminder
from bot.repositories.notes import note_crud
from bot.repositories.reminder import reminder_crud
from bot.repositories.users import user_crud
from bot.services.utils import parse_iso_aware


async def save_note_from_state(
    state: FSMContext,
    session: AsyncSession,
    user_id: int,
    username: str | None,
    message: Message,
):
    """Функция на создание заметки."""
    data = await state.get_data()
    msg_id = data.pop("picker_msg_id")
    chat_id = data.pop("picker_chat_id")

    user = await user_crud.get_user_by_tg_id(user_id, session)
    if not user:
        user = await user_crud.create_object(
            {
                "tg_id": user_id,
                "username": username,
                "chat_id": chat_id,
            },
            session,
        )

    if user.chat_id != chat_id:
        await user_crud.update_obj(user, {"chat_id": chat_id}, session)

    scheduled_at = parse_iso_aware(data.get("remind_at"))

    note_payload = {
        "title": data.get("title", ""),
        "body": data.get("body", None),
    }
    note = await note_crud.create_object(note_payload, session)

    reminder_payload = {
        "note_id": note.id,
        "scheduled_at": scheduled_at,
        "chat_id": chat_id,
        "status": "scheduled",
    }
    await reminder_crud.create_object(reminder_payload, session, user)
    try:
        candidates = [
            IMG_DIR / "save_note.png",
            IMG_DIR / "save_note.PNG",
            IMG_DIR / "save_note.jpg",
            IMG_DIR / "save_note.jpeg",
        ]
        image_path = next((p for p in candidates if p.exists()), None)
        photo = FSInputFile(image_path)
        time = scheduled_at.strftime("%Y-%m-%d %H:%M:%S")
        await message.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=None,
        )

        await message.bot.delete_message(chat_id=chat_id, message_id=msg_id)

        await message.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=("✅ Заметка сохранена\n" f"Время напоминания: {time}"),
        )
    except TelegramBadRequest:
        await message.answer("✅ Заметка сохранена")

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()


async def get_user_notes(
    session: AsyncSession,
    user_tg_id: int,
    limit: int | None = LIMIT_NOTES,
    offset: int | None = 0,
) -> tuple[list[Note], int]:
    user = await user_crud.get_user_by_tg_id(user_tg_id, session)
    if not user:
        user = await user_crud.create_object(
            {"tg_id": user_tg_id},
            session,
        )
    total = await session.scalar(
        select(func.count(Reminder.id))
        .join(Reminder.note)
        .where(Reminder.user_id == user.id)
        .where(
            or_(
                Reminder.status == "scheduled",
                Reminder.status == "queued",
            ),
        ),
    )
    total = int(total or 0)
    stmt = (
        select(Reminder)
        .join(Reminder.note)
        .options(selectinload(Reminder.note))
        .where(Reminder.user_id == user.id)
        .where(Reminder.status.in_(("scheduled", "queued")))
        .order_by(Reminder.scheduled_at.asc())
        .limit(limit)
        .offset(offset)
    )
    reminders = (await session.execute(stmt)).scalars().all()
    notes = [r.note for r in reminders if r.note is not None]
    return notes, total
