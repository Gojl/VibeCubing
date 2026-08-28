import secrets
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.room import Room
from app.db.models.room_member import RoomMember


def generate_room_id() -> str:
    return secrets.token_urlsafe(9)[:12]


async def create_room(
    db: AsyncSession,
    event: str,
    nickname: str,
    color: str,
    user_id: int | None = None,
) -> tuple[Room, RoomMember]:

    now = datetime.now(timezone.utc)

    room = Room(
        id=generate_room_id(),
        event=event,
        created_at=now,
        last_activity_at=now,
    )

    member = RoomMember(
        id=secrets.token_urlsafe(48),
        room_id=room.id,
        user_id=user_id,
        nickname=nickname,
        color=color,
        is_owner=True,
        joined_at=now,
    )

    db.add(room)
    db.add(member)

    await db.commit()

    await db.refresh(room)
    await db.refresh(member)

    return room, member

async def get_room(
    db: AsyncSession,
    room_id: str,
) -> tuple[Room, list[RoomMember]] | None:

    room = await db.get(Room, room_id)

    if room is None:
        return None

    result = await db.execute(
        select(RoomMember).where(RoomMember.room_id == room_id)
    )

    members = list(result.scalars().all())

    return room, members

async def join_room(
    db: AsyncSession,
    room_id: str,
    nickname: str,
    color: str,
    user_id: int | None = None,
) -> RoomMember | None:

    room = await db.get(Room, room_id)

    if room is None:
        return None

    member = RoomMember(
        id=secrets.token_urlsafe(48),
        room_id=room_id,
        user_id=user_id,
        nickname=nickname,
        color=color,
        is_owner=False,
        joined_at=datetime.now(timezone.utc),
    )

    db.add(member)

    room.last_activity_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(member)

    return member


async def leave_room(
    db: AsyncSession,
    room_id: str,
    member_id: str,
) -> str | None:

    room = await db.get(Room, room_id)

    if room is None:
        return None

    member = await db.get(RoomMember, member_id)

    if member is None or member.room_id != room_id:
        return None

    if member.is_owner:
        result = await db.execute(
            select(RoomMember)
            .where(
                RoomMember.room_id == room_id,
                RoomMember.id != member_id,
            )
            .order_by(RoomMember.joined_at.asc())
            .limit(1)
        )
    new_owner = result.scalar_one_or_none()

    if new_owner:
        new_owner.is_owner = True
    else:
        await db.delete(room)
        await db.commit()
        return member_id

    await db.delete(member)
    room.last_activity_at = datetime.now(timezone.utc)
    await db.commit()
    return member_id