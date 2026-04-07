"""Convert quiz_questions to support multi-answer

Revision ID: 004
Revises: 003
Create Date: 2026-04-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "quiz_questions",
        sa.Column("correct_answer_indices", sa.JSON(), nullable=True),
    )
    op.add_column(
        "quiz_questions",
        sa.Column("is_multi", sa.Boolean(), server_default=sa.false(), nullable=False),
    )

    # Migrate existing single-answer rows: wrap correct_answer_index into a JSON array
    op.execute(
        "UPDATE quiz_questions "
        "SET correct_answer_indices = json_build_array(correct_answer_index) "
        "WHERE correct_answer_indices IS NULL"
    )

    op.alter_column("quiz_questions", "correct_answer_indices", nullable=False)
    op.drop_column("quiz_questions", "correct_answer_index")


def downgrade() -> None:
    op.add_column(
        "quiz_questions",
        sa.Column("correct_answer_index", sa.Integer(), nullable=True),
    )
    op.execute(
        "UPDATE quiz_questions "
        "SET correct_answer_index = (correct_answer_indices->>0)::int"
    )
    op.alter_column("quiz_questions", "correct_answer_index", nullable=False)
    op.drop_column("quiz_questions", "is_multi")
    op.drop_column("quiz_questions", "correct_answer_indices")
