import json
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


@router.message(F.web_app_data)
async def handle_webapp(m: Message):
    data = json.loads(m.web_app_data.data)
    await m.answer(f"OK: {data}")
