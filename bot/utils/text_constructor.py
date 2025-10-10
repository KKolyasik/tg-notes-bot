from datetime import datetime

from bot.models import Note


def fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%d.%m.%Y %H:%M") if dt else "—"


def get_text_for_edit_note(note: Note) -> str:
    lines: list[str] = []
    lines.append(f"Заголовок: {note.title or '—'}")

    if note.body:
        lines.append(f"Текст заметки: {note.body}")

    remind_at = None
    reminders = note.reminders

    if not reminders:
        remind_at = None
    elif isinstance(reminders, list):
        future = [r for r in reminders if getattr(r, "scheduled_at", None)]
        future.sort(key=lambda r: r.scheduled_at)
        remind_at = future[0].scheduled_at if future else None
    else:
        remind_at = getattr(reminders, "scheduled_at", None)

    lines.append(f"Время напоминания: {fmt_dt(remind_at)}")

    return "\n".join(lines)
