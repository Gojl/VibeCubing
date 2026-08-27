from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(
        String(12),
        primary_key=True,
    )

    event: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    members: Mapped[list["RoomMember"]] = relationship(
    back_populates="room",
    cascade="all, delete-orphan",
    )

    rounds: Mapped[list["Round"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
    )