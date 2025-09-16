from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)


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
                callback_data="timesnap",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
