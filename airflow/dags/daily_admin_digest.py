from __future__ import annotations

import pendulum
from airflow.sdk import dag, task
from airflow.exceptions import AirflowFailException

from core.constants import BACKEND_URL
from services.http_client import get_json, post_json

BUILD_ENDPOINT = f"{BACKEND_URL}/internal/digest/build"
SEND_ENDPOINT = f"{BACKEND_URL}/internal/digest/send"


@dag(
    dag_id="daily_admin_digest",
    description="Ежедневный админ-дайджест",
    start_date=pendulum.datetime(2025, 10, 1),
    schedule="0 12 * * *",
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": pendulum.duration(minutes=5)},
    tags=["bot", "digest"],
)
def daily_admin_digest():
    @task
    def build_digest(**context) -> dict:
        conf = getattr(context.get("dag_run"), "conf", None) or {}
        params = (
            {"date_iso": conf["date_iso"]}
            if isinstance(conf, dict) and conf.get("date_iso")
            else None
        )
        data = get_json(BUILD_ENDPOINT, params=params)

        for k in ("date", "dau", "new_users", "notes_count", "avg_note_len"):
            if k not in data:
                raise AirflowFailException(f"Digest missing key: {k}")
        return data

    @task
    def send_digest(digest: dict) -> None:
        post_json(SEND_ENDPOINT, digest)

    send_digest(build_digest())


dag = daily_admin_digest()
