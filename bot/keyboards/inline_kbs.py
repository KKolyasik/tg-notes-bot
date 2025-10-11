from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callback import EditNote, NoteOpen, NotesPaginate
from bot.models import Note
from bot.utils.enums import EditNoteAction


def _truncate(text: str, n: int = 32) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def skip_body_note_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="❌Создать заметку без текста",
        callback_data="note:skip_body",
    )
    kb.button(
        text="↩️Отмена",
        сallback_data="decline",
    )
    kb.adjust(1)
    return kb.as_markup()


def get_timesnap() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="⏳ Выбрать время",
        web_app=WebAppInfo(url="https://timesnap.ru/picker"),
    )
    kb.adjust(1)
    return kb.as_markup()


def get_notes_kb(
    notes: list["Note"],
    limit: int,
    offset: int,
    total: int,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if not notes and total == 0:
        kb.row(
            InlineKeyboardButton(text="Заметок нет", callback_data="noop"),
            width=1,
        )
        return kb.as_markup()

    for n in notes:
        kb.row(
            InlineKeyboardButton(
                text=_truncate(n.title),
                callback_data=NoteOpen(note_id=n.id).pack(),
            ),
            width=1,
        )

    nav_buttons: list[InlineKeyboardButton] = []
    if offset > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="« Предыдущая",
                callback_data=NotesPaginate(
                    offset=max(offset - limit, 0),
                ).pack(),
            )
        )
    if offset + limit < total:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Следующая »",
                callback_data=NotesPaginate(offset=offset + limit).pack(),
            )
        )
    if nav_buttons:
        kb.row(*nav_buttons, width=len(nav_buttons))

    total_pages = max((total + limit - 1) // limit, 1)
    cur_page = min(offset // limit + 1, total_pages)
    kb.row(
        InlineKeyboardButton(
            text=f"Стр. {cur_page}/{total_pages}",
            callback_data="noop",
        ),
        width=1,
    )

    return kb.as_markup()


def edit_note_kb(note: Note) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(
        text="Редактировать заголовок",
        callback_data=EditNote(
            note_id=note.id,
            action=EditNoteAction.header,
        ).pack(),
    )

    kb.button(
        text=(
            "Редактировать тело заметки"
            if note.body
            else "Добавить тело заметки"
        ),
        callback_data=EditNote(
            note_id=note.id,
            action=EditNoteAction.body,
        ).pack(),
    )

    kb.button(
        text="Редактировать время заметки",
        callback_data=EditNote(
            note_id=note.id,
            action=EditNoteAction.remind_at,
        ).pack(),
    )

    kb.button(
        text="Удалить заметку",
        callback_data=EditNote(
            note_id=note.id,
            action=EditNoteAction.delete,
        ).pack(),
    )

    kb.button(
        text="↩️Отмена",
        callback_data=EditNote(
            note_id=note.id,
            action=EditNoteAction.decline,
        ).pack(),
    )

    kb.adjust(1)
    return kb.as_markup()
