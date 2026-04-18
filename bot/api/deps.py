from fastapi import Header, HTTPException, status

from bot.core.config import settings


async def service_key_required(
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> bool:
    """Проверка сервисного ключа."""
    if x_api_key != settings.BACKEND_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return True
