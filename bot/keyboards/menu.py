from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="new", description="Создать новую заметку"),
        BotCommand(command="list", description="Показать все заметки"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
