from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def skip_body_note_kb():
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text="❌Создать заметку без текста",
                callback_data="note:skip_body",
            )
        ],
        [
            InlineKeyboardButton(text="↩️Отмена", callback_data="decline")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
