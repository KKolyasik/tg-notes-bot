import math

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from aiogram.filters.callback_data import CallbackData

from bot.models import Note


class NotesPaginate(CallbackData, prefix="np"):
    """Навигация по списку заметок."""

    offset: int


class NoteOpen(CallbackData, prefix="no"):
    """Открыть/редактировать конкретную заметку."""

    note_id: int


def _truncate(text: str, n: int = 32) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def skip_body_note_kb():
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text="❌Создать заметку без текста",
                callback_data="note:skip_body",
            )
        ],
        [InlineKeyboardButton(text="↩️Отмена", callback_data="decline")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def get_timesnap():
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text="⏳ Выбрать время",
                web_app=WebAppInfo(url="https://timesnap.ru/picker"),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def get_notes_kb(
    notes: list[Note],
    limit: int,
    offset: int,
    total: int,
):
    inline_kb_list: list[list[InlineKeyboardButton]] = []

    if not notes:
        inline_kb_list.append([
            InlineKeyboardButton(text="(заметок нет)", callback_data="noop")
        ])

    for note in notes:
        title = _truncate(note.title)
        inline_kb_list.append(
            [
                InlineKeyboardButton(
                    text=title,
                    callback_data=NoteOpen(note_id=note.id).pack(),
                )
            ]
        )
    nav: list[InlineKeyboardButton] = []
    if offset > 0:
        prev_off = max(offset - limit, 0)
        nav.append(
            InlineKeyboardButton(
                text="« Предыдущая",
                callback_data=NotesPaginate(offset=prev_off).pack(),
            )
        )
    if offset + limit < total:
        next_off = offset + limit
        nav.append(
            InlineKeyboardButton(
                text="Следующая »",
                callback_data=NotesPaginate(offset=next_off).pack(),
            )
        )

    if nav:
        inline_kb_list.append(nav)
    total_pages = max(math.ceil(total / limit), 1)
    cur_page = min(offset // limit + 1, total_pages)
    inline_kb_list.append(
        [
            InlineKeyboardButton(
                text=f"Стр. {cur_page}/{total_pages}", callback_data="noop"
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
