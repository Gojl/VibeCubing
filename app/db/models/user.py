from datetime import datetime

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    login: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String,
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

    wca_id: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    nickname_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    color_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    room_members: Mapped[list["RoomMember"]] = relationship(
        back_populates="user",
    )