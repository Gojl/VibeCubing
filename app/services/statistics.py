# from statistics import median as _median

# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.models.room_member import RoomMember
# from app.db.models.round import Round
# from app.db.models.solve import Solve
# from app.schemas.statistics import (
#     HistoryItem,
#     PlayerStats,
#     RoomRecords,
#     RoomStatsResponse,
# )

# HISTORY_LIMIT = 25


# def effective_time(time, penalty: str) -> float | None:
#     """Returns the comparable time in seconds, or None for a DNF."""

#     if penalty == "DNF":
#         return None

#     value = float(time)

#     if penalty == "+2":
#         return value + 2

#     return value


# def format_result(time, penalty: str) -> str:
#     if penalty == "DNF":
#         return "DNF"

#     value = float(time)

#     if penalty == "+2":
#         return f"{value + 2:.2f}+"

#     return f"{value:.2f}"


# def best_average(times: list[float | None], n: int) -> float | None:
#     """Best rolling average of `n` over a chronological sequence of
#     effective times (None = DNF), following the WCA trimmed-mean rule
#     for n >= 5 (drop best and worst, average the rest; more than one
#     DNF in the window makes that window's average invalid)."""

#     if len(times) < n:
#         return None

#     best: float | None = None

#     for start in range(0, len(times) - n + 1):
#         window = times[start:start + n]
#         dnf_count = sum(1 for t in window if t is None)

#         if n < 5:
#             if dnf_count > 0:
#                 continue

#             average = sum(window) / n
#         else:
#             if dnf_count > 1:
#                 continue

#             numeric = sorted(t for t in window if t is not None)

#             # A single DNF in the window counts as the worst result,
#             # so it is one of the two trimmed values already.
#             trimmed = (
#                 numeric[1:-1]
#                 if dnf_count == 0
#                 else numeric[:-1]
#             )

#             if not trimmed:
#                 continue

#             average = sum(trimmed) / len(trimmed)

#         if best is None or average < best:
#             best = average

#     return best


# async def get_room_stats(
#     db: AsyncSession,
#     room_id: str,
# ) -> RoomStatsResponse | None:
#     members_result = await db.execute(
#         select(RoomMember).where(RoomMember.room_id == room_id)
#     )

#     members = list(members_result.scalars().all())

#     if not members:
#         return None

#     member_by_id = {member.id: member for member in members}

#     rows_result = await db.execute(
#         select(Solve, Round)
#         .join(Round, Solve.round_id == Round.id)
#         .where(Round.room_id == room_id)
#         .order_by(Round.number.asc(), Solve.created_at.asc())
#     )

#     rows = rows_result.all()

#     times_by_member: dict[str, list[float | None]] = {
#         member.id: [] for member in members
#     }

#     rounds: dict[int, list[tuple[Solve, Round, float | None]]] = {}

#     for solve, round in rows:
#         effective = effective_time(solve.time, solve.penalty)

#         times_by_member.setdefault(solve.member_id, []).append(effective)

#         rounds.setdefault(round.number, []).append(
#             (solve, round, effective)
#         )

#     # --- Room records (best across all members) ---

#     records = RoomRecords()

#     all_singles = [
#         t
#         for times in times_by_member.values()
#         for t in times
#         if t is not None
#     ]

#     if all_singles:
#         records.single = min(all_singles)

#     for n, field in (
#         (5, "ao5"),
#         (12, "ao12"),
#         (25, "ao25"),
#         (50, "ao50"),
#         (100, "ao100"),
#     ):
#         member_bests = [
#             best_average(times, n)
#             for times in times_by_member.values()
#         ]

#         member_bests = [b for b in member_bests if b is not None]

#         if member_bests:
#             setattr(records, field, min(member_bests))

#     # --- Per-player stats ---

#     wins: dict[str, int] = {member.id: 0 for member in members}

#     for round_number, entries in rounds.items():
#         finished = [
#             (solve, effective)
#             for solve, round, effective in entries
#             if effective is not None
#         ]

#         if not finished:
#             continue

#         winner_solve, _ = min(finished, key=lambda item: item[1])
#         wins[winner_solve.member_id] = wins.get(winner_solve.member_id, 0) + 1

#     players = []

#     for member in members:
#         numeric_times = [
#             t for t in times_by_member.get(member.id, []) if t is not None
#         ]

#         players.append(
#             PlayerStats(
#                 member_id=member.id,
#                 nickname=member.nickname,
#                 wins=wins.get(member.id, 0),
#                 median=_median(numeric_times) if numeric_times else None,
#             )
#         )

#     players.sort(key=lambda p: (-p.wins, p.median is None, p.median or 0))

#     # --- History (most recent completed rounds first) ---

#     history = []

#     for round_number in sorted(rounds.keys(), reverse=True):
#         entries = rounds[round_number]
#         finished = [
#             (solve, effective)
#             for solve, round, effective in entries
#             if effective is not None
#         ]

#         if not finished:
#             continue

#         winner_solve, _ = min(finished, key=lambda item: item[1])
#         winner_member = member_by_id.get(winner_solve.member_id)

#         if winner_member is None:
#             continue

#         history.append(
#             HistoryItem(
#                 round=round_number,
#                 nickname=winner_member.nickname,
#                 result=format_result(
#                     winner_solve.time, winner_solve.penalty
#                 ),
#             )
#         )

#         if len(history) >= HISTORY_LIMIT:
#             break

#     return RoomStatsResponse(
#         records=records,
#         players=players,
#         history=history,
#     )