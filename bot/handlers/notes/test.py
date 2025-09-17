import json
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    Message,
)


kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏳ Выбрать время",
                              web_app=WebAppInfo(url="https://timesnap.ru/picker"))]],
    resize_keyboard=True, is_persistent=True,
)


router = Router()


@router.message(Command("testpicker"))
async def testpicker(m: Message):
    await m.answer("Открываю пикер", reply_markup=kb)


@router.message(F.web_app_data)
async def handle_webapp(m: Message):
    data = json.loads(m.web_app_data.data)
    await m.answer(f"OK: {data}")
