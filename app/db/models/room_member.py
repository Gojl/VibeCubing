from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class RoomMember(Base):
    __tablename__ = "room_members"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    room_id: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    nickname: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    color: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
    )

    is_owner: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    room: Mapped["Room"] = relationship(
    back_populates="members",
    )

    user: Mapped["User | None"] = relationship(
        back_populates="room_members",
    )

    solves: Mapped[list["Solve"]] = relationship(
        back_populates="member",
    )