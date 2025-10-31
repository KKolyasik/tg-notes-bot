from datetime import datetime

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.core.config import settings
from bot.models.user import User
from bot.schemas.digest import DailyDigest


def parse_iso_aware(iso_time: str) -> datetime:
    """Парсит данные из iso формата в aware datetime."""
    dt = datetime.fromisoformat(iso_time)
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone aware")
    return dt


def make_bot() -> Bot:
    """Создает экземпляр бота."""
    return Bot(
        settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def check_chat_id(
    user: User,
    current_chit_id: int,
) -> bool:
    return user.chat_id == current_chit_id


def format_digest_html(digest: DailyDigest) -> str:
    lines = [
        f"<b>Ежедневный дайджест</b> — {digest.date}",
        "",
        f"👥 DAU: <b>{digest.dau}</b>",
        f"🆕 Новых пользователей: <b>{digest.new_users}</b>",
        f"🗒️ Всего заметок: <b>{digest.notes_count}</b>",
        f"✍️ Средняя длина заголовка: <b>{digest.avg_note_len:.1f}</b>",
    ]
    if digest.errors_count is not None:
        lines.append(f"⚠️ Ошибок: <b>{digest.errors_count}</b>")

    if digest.top_users:
        lines.append("")
        lines.append("<b>Топ-5 по заметкам:</b>")
        for i, tu in enumerate(digest.top_users, start=1):
            uname = tu.username or "—"
            lines.append(
                f"{i}. {uname} (id={tu.user_id}) — <b>{tu.notes_count}</b>",
            )
    return "\n".join(lines)
