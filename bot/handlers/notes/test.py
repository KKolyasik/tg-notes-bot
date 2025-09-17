from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    Message,
)


kb = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="⏳ Выбрать время",
        web_app=WebAppInfo(url="https://timesnap.ru/picker")
    )
]])


router = Router()


@router.message(Command("testpicker"))
async def testpicker(m: Message):
    await m.answer("Открываю пикер", reply_markup=kb)


@router.message()
async def handle_webapp(m: Message):
    data = m.text
    await m.answer(f"OK: {data}")
