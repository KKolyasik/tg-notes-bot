from datetime import datetime


def parse_iso_aware(iso_time: str) -> datetime:
    """Парсит данные из iso формата в aware datetime."""
    dt = datetime.fromisoformat(iso_time)
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return dt
