from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.solve import CreateSolveRequest, SolveResponse
from app.services.rounds import (
    create_round,
    get_current_round,
)
from app.services.solve import (
    create_solve,
    get_round_solves,
)
from app.websocket.manager import manager
from app.db.database import get_db
from app.schemas.room import (
    CreateRoomRequest,
    CreateRoomResponse,
    JoinRoomRequest,
    JoinRoomResponse,
    LeaveRoomResponse,
    RoomMemberResponse,
    RoomResponse,
)
from app.schemas.round import RoundResponse
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

    await manager.broadcast(
        room_id,
        {
            "type": "member_joined",
            "member": {
                "id": member.id,
                "nickname": member.nickname,
                "color": member.color,
                "is_owner": member.is_owner,
            },
        },
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

    await manager.broadcast(
        room_id,
        {
            "type": "member_left",
            "member_id": member_id,
        },
    )

    return LeaveRoomResponse(
        message="Left room successfully",
    )

@router.post(
    "/{room_id}/rounds",
    response_model=RoundResponse,
)
async def create_round_endpoint(
    room_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        round = await create_round(
            db=db,
            room_id=room_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    return round

@router.get(
    "/{room_id}/rounds/current",
    response_model=RoundResponse,
)
async def get_current_round_endpoint(
    room_id: str,
    db: AsyncSession = Depends(get_db),
):
    current_round = await get_current_round(
        db=db,
        room_id=room_id,
    )

    if current_round is None:
        raise HTTPException(
            status_code=404,
            detail="No active round",
        )

    return current_round

@router.post(
    "/{room_id}/rounds/{round_id}/solves",
    response_model=SolveResponse,
)
async def create_solve_endpoint(
    room_id: str,
    round_id: int,
    data: CreateSolveRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await create_solve(
            db=db,
            room_id=room_id,
            round_id=round_id,
            member_id=data.member_id,
            time=data.time,
            penalty=data.penalty,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Round or member not found",
        )

    solve, round_completed = result

    await manager.broadcast(
        room_id,
        {
            "type": "solve_submitted",
            "round_id": solve.round_id,
            "member_id": solve.member_id,
            "time": float(solve.time),
            "penalty": solve.penalty,
        },
    )

    if round_completed:

        current_round = await get_current_round(
            db=db,
            room_id=room_id,
        )

        if current_round:

            await manager.broadcast(
                room_id,
                {
                    "type": "round_started",
                    "round_id": current_round.id,
                    "number": current_round.number,
                    "scramble": current_round.scramble,
                },
            )

    return SolveResponse(
        id=solve.id,
        round_id=solve.round_id,
        member_id=solve.member_id,
        time=solve.time,
        penalty=solve.penalty,
        created_at=solve.created_at,
        updated_at=solve.updated_at,
    )   

@router.get(
    "/{room_id}/rounds/{round_id}/solves",
    response_model=list[SolveResponse],
)
async def get_round_solves_endpoint(
    room_id: str,
    round_id: int,
    db: AsyncSession = Depends(get_db),
):
    solves = await get_round_solves(
        db=db,
        room_id=room_id,
        round_id=round_id,
    )

    return solves