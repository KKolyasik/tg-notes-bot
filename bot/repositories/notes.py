from bot.models import Note
from bot.repositories.base import CRUDBase


class CRUDNotes(CRUDBase[Note]):
    pass


note_crud = CRUDNotes(Note)
