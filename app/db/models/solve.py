from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Solve(Base):
    __tablename__ = "solves"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    round_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rounds.id", ondelete="CASCADE"),
        nullable=False,
    )

    member_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("room_members.id", ondelete="CASCADE"),
        nullable=False,
    )

    time: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    penalty: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="none",
        server_default="none",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    round: Mapped["Round"] = relationship(
    back_populates="solves",
    )

    member: Mapped["RoomMember"] = relationship(
        back_populates="solves",
    )