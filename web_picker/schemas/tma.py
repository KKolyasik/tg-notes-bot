from pydantic import BaseModel, Field


class SubmitPayload(BaseModel):
    iso_utc: str = Field(..., description="ISO время в UTC от клиента")
    local: str | None
    tz_offset_min: int | None = None
    step_min: int | None = None
    query_id: str
    init_data: str | None = None
    note_id: int | None = None
