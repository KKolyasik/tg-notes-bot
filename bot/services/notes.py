from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.exceptions import TelegramBadRequest

from bot.main import STATIC_DIR
from bot.repositories.users import user_crud
from bot.repositories.notes import note_crud
from bot.repositories.reminder import reminder_crud
from bot.services.utils import parse_iso_aware


async def save_note_from_state(
    state: FSMContext,
    session: AsyncSession,
    user_id: int,
    message: Message,
):
    """Функция на создание заметки."""
    data = await state.get_data()
    msg_id = data.pop("picker_msg_id")
    chat_id = data.pop("picker_chat_id")

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
    try:
        image_path = STATIC_DIR / "images" / "save_note.png"
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
            caption=(
                "✅ Заметка сохранена\n"
                f"Время напоминания: {time}"
            ),
        )
    except TelegramBadRequest:
        await message.answer("✅ Заметка сохранена")

    try:
        message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
