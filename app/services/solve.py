from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.round import Round
from app.db.models.room_member import RoomMember
from app.db.models.solve import Solve
from app.schemas.solve import Penalty
from app.services.rounds import create_round


async def create_solve(
    db: AsyncSession,
    room_id: str,
    round_id: int,
    member_id: str,
    time: float,
    penalty: Penalty,
):
    # Sprawdzenie rundy
    result = await db.execute(
        select(Round).where(
            Round.id == round_id,
            Round.room_id == room_id,
        )
    )

    round = result.scalar_one_or_none()

    if round is None:
        return None

    # Sprawdzenie członka pokoju
    result = await db.execute(
        select(RoomMember).where(
            RoomMember.id == member_id,
            RoomMember.room_id == room_id,
        )
    )

    member = result.scalar_one_or_none()

    if member is None:
        return None

    # Sprawdzenie, czy członek już wysłał solve
    result = await db.execute(
        select(Solve).where(
            Solve.round_id == round_id,
            Solve.member_id == member_id,
        )
    )

    existing_solve = result.scalar_one_or_none()

    if existing_solve is not None:
        raise ValueError(
            "Member already submitted a solve for this round"
        )

    now = datetime.now(timezone.utc)

    solve = Solve(
        round_id=round_id,
        member_id=member_id,
        time=time,
        penalty=penalty.value,
        created_at=now,
        updated_at=now,
    )

    db.add(solve)

    # Musimy zapisać solve do sesji,
    # żeby COUNT() go uwzględnił.
    await db.flush()

    # Liczba członków pokoju
    result = await db.execute(
        select(func.count(RoomMember.id)).where(
            RoomMember.room_id == room_id
        )
    )

    member_count = result.scalar_one()

    # Liczba solve'ów w tej rundzie
    result = await db.execute(
        select(func.count(Solve.id)).where(
            Solve.round_id == round_id
        )
    )

    solve_count = result.scalar_one()

    round_completed = False

    # Runda kończy się dopiero wtedy,
    # gdy KAŻDY członek ma solve.
    if (
        round.completed_at is None
        and solve_count >= member_count
    ):
        round.completed_at = now
        round_completed = True

    await db.commit()
    await db.refresh(solve)

    # Dopiero po zakończeniu rundy tworzymy następną.
    if round_completed:
        await create_round(
            db=db,
            room_id=room_id,
        )

    return solve, round_completed


async def get_round_solves(
    db: AsyncSession,
    room_id: str,
    round_id: int,
):
    result = await db.execute(
        select(Solve)
        .join(Round, Solve.round_id == Round.id)
        .where(
            Round.id == round_id,
            Round.room_id == room_id,
        )
        .order_by(Solve.created_at)
    )

    return result.scalars().all()