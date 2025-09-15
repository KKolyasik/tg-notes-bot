from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.text_kbs import main_kb

router = Router(name="Стартовый роутер")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Запуск сообщения по команде /start используя фильтр CommandStart()",
        reply_markup=main_kb(),
    )
