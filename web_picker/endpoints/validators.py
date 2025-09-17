import hmac
import hashlib
from urllib.parse import parse_qsl


def _data_check_string(init_data: str) -> tuple[str, str]:
    """
    Возвращает (data_check_string, hash_from_query)
    Алгоритм по доке Telegram Mini Apps.
    """
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = params.pop("hash", "")
    # сортируем по ключу и собираем "key=value" построчно
    parts = [
        f"{k}={v}"
        for k, v in sorted(
            params.items(),
            key=lambda kv: kv[0],
        )
    ]
    return "\n".join(parts), received_hash


def validate_init_data(init_data: str, bot_token: str) -> bool:
    """
    secret_key = HMAC_SHA256(key="WebAppData", data=bot_token)
    check_hash = HMAC_SHA256(key=secret_key, data=data_check_string)
    compare with hash (hex) из initData
    """
    data_check_string, received_hash = _data_check_string(init_data)
    if not received_hash:
        return False

    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256,
    ).digest()
    calc_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(calc_hash, received_hash)
