from datetime import UTC, datetime


def correct_time(remind_at: datetime) -> bool:
    """Проверяет корректность напоминания."""
    now = (
        datetime.now(remind_at.tzinfo)
        if remind_at.tzinfo
        else datetime.now(UTC)
    )
    return remind_at >= now
