from bot.models import Reminder
from bot.repositories.base import CRUDBase


class CRUDReminder(CRUDBase[Reminder]):

    pass


reminder_crud = CRUDReminder(Reminder)
