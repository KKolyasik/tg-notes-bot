from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.constants import BTN_CREATE, BTN_LIST


def main_kb():
    kb_list = [
        [
            KeyboardButton(text=BTN_CREATE),
            KeyboardButton(text=BTN_LIST),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
    )
