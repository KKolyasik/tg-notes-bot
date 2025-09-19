from celery import Celery

from bot.core.config import settings
from bot.celery.tasks import check_reminders
from bot.constants import TIME_TO_SCHEDULE


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
)


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(TIME_TO_SCHEDULE, check_reminders.s(15))
