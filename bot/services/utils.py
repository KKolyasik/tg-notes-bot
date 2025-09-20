from datetime import datetime

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.core.config import settings


def parse_iso_aware(iso_time: str) -> datetime:
    """Парсит данные из iso формата в aware datetime."""
    dt = datetime.fromisoformat(iso_time)
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return dt


def make_bot(token: str = settings.BOT_TOKEN) -> Bot:
    """Создает экземпляр бота"""
    return Bot(
        token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
