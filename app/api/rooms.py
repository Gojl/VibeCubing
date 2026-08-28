from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db
from app.schemas.room import CreateRoomRequest, CreateRoomResponse
from app.services.rooms import create_room
from app.services.rooms import create_room, get_room
from app.services.rooms import create_room, get_room, join_room
from app.schemas.room import (
    CreateRoomRequest,
    CreateRoomResponse,
    JoinRoomRequest,
    JoinRoomResponse,
    LeaveRoomResponse,
    RoomMemberResponse,
    RoomResponse,
)
from app.services.rooms import (
    create_room,
    get_room,
    join_room,
    leave_room,
)


router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=CreateRoomResponse)
async def create_room_endpoint(
    data: CreateRoomRequest,
    db: AsyncSession = Depends(get_db),
):
    room, member = await create_room(
        db=db,
        event=data.event,
        nickname=data.nickname,
        color=data.color,
        user_id=data.user_id,
    )

    return CreateRoomResponse(
        room_id=room.id,
        member_id=member.id,
    )

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room_endpoint(
    room_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await get_room(db, room_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    room, members = result

    return RoomResponse(
        id=room.id,
        event=room.event,
        members=[
            RoomMemberResponse(
                id=member.id,
                nickname=member.nickname,
                color=member.color,
                is_owner=member.is_owner,
            )
            for member in members
        ],
    )

@router.post("/{room_id}/join", response_model=JoinRoomResponse)
async def join_room_endpoint(
    room_id: str,
    data: JoinRoomRequest,
    db: AsyncSession = Depends(get_db),
):
    member = await join_room(
        db=db,
        room_id=room_id,
        nickname=data.nickname,
        color=data.color,
    )

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    return JoinRoomResponse(
        member_id=member.id,
    )

@router.delete(
    "/{room_id}/members/{member_id}",
    response_model=LeaveRoomResponse,
)
async def leave_room_endpoint(
    room_id: str,
    member_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await leave_room(
            db=db,
            room_id=room_id,
            member_id=member_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Room or member not found",
        )

    return LeaveRoomResponse(
        message="Left room successfully",
    )