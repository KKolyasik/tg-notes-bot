from app.models import Note
from app.repositories.base import CRUDBase


class CRUDNotes(CRUDBase):
    pass


note_crud = CRUDNotes(Note)
