from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

from bot.keyboards.callback import EditNote, NoteOpen, NotesPaginate
from bot.models import Note
from bot.utils.enums import EditNoteAction


def _truncate(text: str, n: int = 32) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def skip_body_note_kb() -> InlineKeyboardMarkup:
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text="❌Создать заметку без текста",
                callback_data="note:skip_body",
            ),
        ],
        [InlineKeyboardButton(text="↩️Отмена", callback_data="decline")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def get_timesnap() -> InlineKeyboardMarkup:
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text="⏳ Выбрать время",
                web_app=WebAppInfo(url="https://timesnap.ru/picker"),
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def get_notes_kb(
    notes: list[Note],
    limit: int,
    offset: int,
    total: int,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    if not notes and total == 0:
        rows.append(
            [
                InlineKeyboardButton(
                    text="(заметок нет)",
                    callback_data="noop",
                ),
            ],
        )

    for n in notes:
        title = _truncate(n.title)
        rows.append(
            [
                InlineKeyboardButton(
                    text=title,
                    callback_data=NoteOpen(note_id=n.id).pack(),
                ),
            ],
        )

    nav: list[InlineKeyboardButton] = []
    if offset > 0:
        nav.append(
            InlineKeyboardButton(
                "« Предыдущая",
                callback_data=NotesPaginate(
                    offset=max(offset - limit, 0),
                ).pack(),
            ),
        )
    if offset + limit < total:
        nav.append(
            InlineKeyboardButton(
                "Следующая »",
                callback_data=NotesPaginate(offset=offset + limit).pack(),
            ),
        )
    if nav:
        rows.append(nav)

    total_pages = max((total + limit - 1) // limit, 1)
    cur_page = min(offset // limit + 1, total_pages)
    rows.append(
        [
            InlineKeyboardButton(
                text=f"Стр. {cur_page}/{total_pages}",
                callback_data="noop",
            ),
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def edit_note_kb(note: Note) -> InlineKeyboardMarkup:
    kb_list = [
        [
            InlineKeyboardButton(
                text="Редактировать заголовок",
                callback_data=EditNote(
                    note_id=note.id,
                    action=EditNoteAction.header,
                ).pack(),
            ),
        ],
    ]
    if note.body is not None:
        kb_list.append(
            [
                InlineKeyboardButton(
                    text="Редактировать тело заметки",
                    callback_data=EditNote(
                        note_id=note.id,
                        action=EditNoteAction.body,
                    ).pack(),
                ),
            ],
        )

    kb_list.append(
        [
            InlineKeyboardButton(
                text="Редактировать время заметки",
                callback_data=EditNote(
                    note_id=note.id,
                    action=EditNoteAction.remind_at,
                ).pack(),
            ),
        ],
    )

    kb_list.append(
        [InlineKeyboardButton(text="↩️Отмена", callback_data="decline")],
    )

    return InlineKeyboardMarkup(inline_keyboard=kb_list)
