from enum import StrEnum


class EditNoteAction(StrEnum):
    header = "header"
    body = "body"
    remind_at = "remind_at"
    decline = "decline"
