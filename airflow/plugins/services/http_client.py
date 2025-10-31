import json
import requests
from typing import Any, Dict, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from core.constants import API_KEY, HTTP_TIMEOUT

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    retry = Retry(
        total=4,
        backoff_factor=1.0,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    with get_session() as session:
        request = session.get(url, params=params, timeout=HTTP_TIMEOUT)
    request.raise_for_status()
    try:
        return request.json()
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Bad JSON from {url}: {e}") from e


def post_json(url: str, payload: Dict[str, Any]) -> None:
    with get_session() as session:
        request = session.post(url, json=payload, timeout=HTTP_TIMEOUT)
    request.raise_for_status()
