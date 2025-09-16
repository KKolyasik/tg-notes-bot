from bot.models import Note
from bot.repositories.base import CRUDBase


class CRUDNotes(CRUDBase):
    pass


note_crud = CRUDNotes(Note)
