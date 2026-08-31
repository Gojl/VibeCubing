from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class Penalty(str, Enum):
    NONE = "none"
    PLUS_TWO = "+2"
    DNF = "DNF"

class CreateSolveRequest(BaseModel):
    member_id: str
    time: float
    penalty: Penalty = Penalty.NONE


class SolveResponse(BaseModel):
    id: int
    round_id: int
    member_id: str
    time: float
    penalty: str
    created_at: datetime
    updated_at: datetime