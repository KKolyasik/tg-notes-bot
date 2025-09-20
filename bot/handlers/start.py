from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.text_kbs import main_kb

router = Router(name="Стартовый роутер")


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "<b><i><u>🙌 Хэй! Это «Planerka» 📅</u></i></b>\n"
        "Здесь всё по плану: создавай заметки и получай напоминания вовремя 🚀"
    )
    await message.answer(
        text,
        reply_markup=main_kb(),
    )
