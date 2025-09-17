from datetime import datetime
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

    # ВАЛИДАЦИЯ initData (очень рекомендуется)
    if not validate_init_data(init_data, settings.BOT_TOKEN):
        raise HTTPException(
            status_code=403,
            detail="invalid init_data signature",
        )

    # Парсим время
    try:
        when = datetime.fromisoformat(payload.iso_utc.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=400, detail="bad iso_utc")

    # Тут можно сохранить/запланировать реальную джобу напоминания (БД/очередь)
    # ...

    # Красивый текст сообщения в чат
    text = f"🔔 Напоминание установлено на {when:%d.%m %H:%M} (UTC)"
    if payload.local:
        text += f"\n(локально: {payload.local})"
    if payload.note_id:
        text += f"\nЗаметка: #{payload.note_id}"

    # Отрисовываем сообщение в чат, из которого открыли WebApp
    try:
        await answer_web_app_query(
            bot_token=settings.BOT_TOKEN,
            query_id=payload.query_id,
            title="Напоминание создано",
            message_text=text,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"telegram error: {e}")

    return {"ok": True}
