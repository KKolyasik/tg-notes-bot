from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router(name="Создание заметки")


class NewNote(StatesGroup):
    title = State()
    body = State()


async def cmd_new(message: Message, state: FSMContext):
    await state.set_state(NewNote.title)
    await message.answer("Заголовок заметки?")
