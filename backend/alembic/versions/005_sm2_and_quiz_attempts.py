"""Add SM-2 fields to flashcards and quiz_attempts table

Revision ID: 005
Revises: 004
Create Date: 2026-04-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SM-2 fields on flashcards
    op.add_column(
        "flashcards",
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
    )
    op.add_column(
        "flashcards",
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "flashcards",
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "flashcards",
        sa.Column(
            "next_review_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # quiz_attempts table
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "quiz_id",
            sa.Integer(),
            sa.ForeignKey("quizzes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("quiz_attempts")
    op.drop_column("flashcards", "next_review_at")
    op.drop_column("flashcards", "repetitions")
    op.drop_column("flashcards", "interval_days")
    op.drop_column("flashcards", "ease_factor")
