from aiogram import Bot


def create_message(title: str, body: str) -> str:
    """Создает из заголовка и тела сообщение для отправки."""
    title = (title or "").strip()
    body = (body or "").strip()
    if body:
        return f"🔔 Напоминание\n{title}\n\n{body}"
    return f"🔔 Напоминание\n{title}"


def make_bot(token: str) -> Bot:
    return Bot(token=token, parse_mode=None)
