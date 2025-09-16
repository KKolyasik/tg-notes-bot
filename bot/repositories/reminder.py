from bot.repositories.base import CRUDBase
from bot.models import Reminder


class CRUDReminder(CRUDBase):
    pass


reminder_crud = CRUDReminder(Reminder)
