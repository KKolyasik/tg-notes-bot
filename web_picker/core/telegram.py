import json
import httpx


TELEGRAM_API = "https://api.telegram.org"


async def answer_web_app_query(
    bot_token: str,
    query_id: str,
    title: str,
    message_text: str,
    disable_web_page_preview: bool = True,
    parse_mode: str | None = "HTML",
):
    """
    POST /bot<token>/answerWebAppQuery
    result — это любой InlineQueryResult (дадим article).
    """
    result_obj = {
        "type": "article",
        "id": "reminder-ok",  # может быть любой уникальный ID
        "title": title,
        "input_message_content": {
            "message_text": message_text,
            **({"parse_mode": parse_mode} if parse_mode else {}),
            **(
                {
                    "disable_web_page_preview": True,
                }
                if disable_web_page_preview
                else {}
            ),
        },
        # можно добавить описание/миниатюру, если хочется
    }

    url = f"{TELEGRAM_API}/bot{bot_token}/answerWebAppQuery"
    data = {
        "web_app_query_id": query_id,
        "result": json.dumps(result_obj, ensure_ascii=False),
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, data=data)
        r.raise_for_status()
        return r.json()
