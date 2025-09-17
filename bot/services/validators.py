from datetime import datetime


def correct_time(remind_at: datetime) -> bool:
    """Проверяет корректность напоминания."""
    if remind_at.tzinfo:
        now = datetime.now(remind_at.tzinfo)
    else:
        now = datetime.now()
    return remind_at >= now
