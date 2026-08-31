from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoundResponse(BaseModel):
    id: int
    room_id: str
    number: int
    scramble: str
    started_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)