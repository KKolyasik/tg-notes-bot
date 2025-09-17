from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Header
from web_picker.schemas.tma import SubmitPayload
from web_picker.core.config import settings
from web_picker.endpoints.validators import validate_init_data
from web_picker.core.telegram import answer_web_app_query

router = APIRouter(prefix="/tma", tags=["tma"])


@router.post("/submit")
async def submit(
    payload: SubmitPayload,
    x_telegram_init_data: str | None = Header(default=None),
):
    """
    Принимаем данные из WebApp (inline), валидируем initData,
    отвечаем через answerWebAppQuery.
    """
    init_data = payload.init_data or x_telegram_init_data
    if not init_data:
        raise HTTPException(status_code=400, detail="init_data is required")

    if not validate_init_data(init_data, settings.BOT_TOKEN):
        raise HTTPException(
            status_code=403,
            detail="invalid init_data signature",
        )

    try:
        local_str = payload.local
        offset_min = payload.tz_offset_min
    except Exception:
        raise HTTPException(status_code=400, detail="bad iso_utc format")

    offset = timezone(timedelta(minutes=offset_min))
    local_dt = datetime.fromisoformat(local_str).replace(tzinfo=offset)
    iso_local = local_dt.isoformat(timespec="minutes")

    try:
        await answer_web_app_query(
            settings.BOT_TOKEN,
            payload.query_id,
            iso_local,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"telegram error: {e}")

    return {"ok": True}
