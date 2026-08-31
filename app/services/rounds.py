from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.room import Room
from app.db.models.round import Round
from app.services.scramble import generate_scramble


async def create_round(
    db: AsyncSession,
    room_id: str,
) -> Round:

    result = await db.execute(
        select(Room).where(Room.id == room_id)
    )

    room = result.scalar_one_or_none()

    if room is None:
        raise ValueError("Room not found")

    result = await db.execute(
        select(Round)
        .where(Round.room_id == room_id)
        .order_by(Round.number.desc())
    )

    last_round = result.scalars().first()

    if last_round is None:
        number = 1
    else:
        number = last_round.number + 1

    now = datetime.now(timezone.utc)

    round = Round(
        room_id=room_id,
        number=number,
        scramble=generate_scramble(),
        started_at=now,
    )

    db.add(round)

    room.last_activity_at = now

    await db.commit()
    await db.refresh(round)

    return round


async def get_current_round(
    db: AsyncSession,
    room_id: str,
):
    result = await db.execute(
        select(Round)
        .where(
            Round.room_id == room_id,
            Round.completed_at.is_(None),
        )
        .order_by(Round.number.desc())
    )

    return result.scalars().first()