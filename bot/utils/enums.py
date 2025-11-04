from enum import StrEnum


class EditNoteAction(StrEnum):
    """Enum класс для выбора редактирования."""
    header = "header"
    body = "body"
    remind_at = "remind_at"
    decline = "decline"
    delete = "delete"
