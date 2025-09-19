from celery import Celery
from celery.signals import worker_process_init, worker_shutdown

from bot.core.config import settings
from bot.celery.tasks import check_reminders
from bot.constants import TIME_TO_SCHEDULE
from bot.celery.aloop import start_loop, stop_loop, run_coro
from bot.celery.adb import init_async_db, dispose_async_db


class MyCelery(Celery):

    def gen_task_name(self, name: str, module: str) -> str:
        if module.endswith(".tasks"):
            module = module[:-6]
        return super().gen_task_name(name, module)


app = MyCelery("notes", broker=settings.redis_url(1))

app.conf.update(
    task_acks_late=True,
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "bot.celery.tasks.check_reminders": {"queue": "maintenance"},
        "bot.celery.tasks.send_reminder": {"queue": "reminders"},
    },
)


@worker_process_init.connect
def on_worker_proc_init(**kwargs):
    start_loop()
    run_coro(init_async_db(settings.db_url))


@worker_shutdown.connect
def on_worker_shutdown(**kwargs):
    run_coro(dispose_async_db())
    stop_loop()


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        TIME_TO_SCHEDULE,
        check_reminders.s(15),
        queue="maintenance",
        name="plan-reminders",
    )
