from pydantic import BaseModel


class TopUser(BaseModel):
    user_id: int
    username: str
    notes_count: int


class DailyDigest(BaseModel):
    date: str
    dau: int
    new_users: int
    notes_count: int
    avg_note_len: float
    top_users: list[TopUser]
    errors_count: int
