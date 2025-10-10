from aiogram.filters.callback_data import CallbackData

from bot.utils.enums import EditNoteAction


class NotesPaginate(CallbackData, prefix="np"):
    """Навигация по списку заметок."""

    offset: int


class NoteOpen(CallbackData, prefix="no"):
    """Открыть/редактировать конкретную заметку."""

    note_id: int


class EditNote(CallbackData, prefix="edit"):
    note_id: int
    action: EditNoteAction
