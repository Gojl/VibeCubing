from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Round(Base):
    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    room_id: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
    )

    number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    scramble: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    room: Mapped["Room"] = relationship(
    back_populates="rounds",
    )

    solves: Mapped[list["Solve"]] = relationship(
        back_populates="round",
        cascade="all, delete-orphan",
    )