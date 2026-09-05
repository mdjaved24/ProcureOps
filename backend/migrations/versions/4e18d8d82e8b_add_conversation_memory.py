"""add conversation memory

Revision ID: 4e18d8d82e8b
Revises: 0ed04eccc59e
Create Date: 2026-09-02 20:37:57.236887

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.

revision: str = "4e18d8d82e8b"
down_revision: Union[str, Sequence[str], None] = "0ed04eccc59e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "conversation_memories",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "thread_id",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "memory_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_conversation_memories_id"),
        "conversation_memories",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_conversation_memories_user_id"),
        "conversation_memories",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_conversation_memories_thread_id"),
        "conversation_memories",
        ["thread_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_conversation_memories_memory_type"),
        "conversation_memories",
        ["memory_type"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_conversation_memories_memory_type"),
        table_name="conversation_memories",
    )

    op.drop_index(
        op.f("ix_conversation_memories_thread_id"),
        table_name="conversation_memories",
    )

    op.drop_index(
        op.f("ix_conversation_memories_user_id"),
        table_name="conversation_memories",
    )

    op.drop_index(
        op.f("ix_conversation_memories_id"),
        table_name="conversation_memories",
    )

    op.drop_table("conversation_memories")