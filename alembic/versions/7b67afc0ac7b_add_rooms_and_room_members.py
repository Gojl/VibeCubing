"""add rooms and room members

Revision ID: 7b67afc0ac7b
Revises: 4d64161b6cd8
Create Date: 2026-08-27 14:45:34.111808
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b67afc0ac7b"
down_revision: Union[str, Sequence[str], None] = "4d64161b6cd8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "rooms",
        sa.Column("id", sa.String(length=12), nullable=False),
        sa.Column("event", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "room_members",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("room_id", sa.String(length=12), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("nickname", sa.String(length=32), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False),
        sa.Column(
            "is_owner",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("room_members")
    op.drop_table("rooms")