from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    event: str = Field(min_length=1, max_length=32)
    nickname: str = Field(min_length=1, max_length=32)
    color: str = Field(min_length=7, max_length=7)
    user_id: int | None = None


class CreateRoomResponse(BaseModel):
    room_id: str
    member_id: str


class RoomMemberResponse(BaseModel):
    id: str
    nickname: str
    color: str
    is_owner: bool


class RoomResponse(BaseModel):
    id: str
    event: str
    members: list[RoomMemberResponse]

class JoinRoomRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=32)
    color: str = Field(min_length=7, max_length=7)


class JoinRoomResponse(BaseModel):
    member_id: str

class LeaveRoomResponse(BaseModel):
    message: str