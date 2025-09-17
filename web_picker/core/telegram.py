import httpx


TELEGRAM_API = "https://api.telegram.org"


async def answer_web_app_query(bot_token: str, query_id: str, iso_utc: str):
    """Функция для оправки сообщения в чат со временем напоминания."""
    result_query = {
        "type": "article",
        "id": query_id,
        "title": "ISO time",
        "input_message_content": {"message_text": iso_utc},
    }

    url = f"{TELEGRAM_API}/bot{bot_token}/answerWebAppQuery"
    payload = {
        "web_app_query_id": query_id,
        "result": result_query,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url=url, json=payload)
        response.raise_for_status()
        return response.json()
