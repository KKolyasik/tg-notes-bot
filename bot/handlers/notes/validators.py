from datetime import datetime


def correct_time(remind_at: datetime):
    """Проверяет корректность напоминания."""
    if remind_at < datetime.now():
        return False
    return True
