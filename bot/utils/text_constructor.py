from datetime import datetime

from bot.models import Note


def fmt_dt(dt: datetime | None) -> str:
    """Преобразование времени в строку с нужным форматом."""
    return dt.strftime("%d.%m.%Y %H:%M") if dt else "—"


def get_text_for_edit_note(note: Note) -> str:
    """Функция для формиравания сообщения для редактирования заметки."""
    lines: list[str] = []
    lines.append(f"Заголовок: {note.title or '—'}")

    if note.body:
        lines.append(f"Текст заметки: {note.body}")

    remind_at = note.reminder.scheduled_at

    lines.append(f"Время напоминания: {fmt_dt(remind_at)}")

    return "\n".join(lines)
