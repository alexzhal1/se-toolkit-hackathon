"""Replace telegram_id with email, login, hashed_password in users; drop login_tokens

Revision ID: 006
Revises: 005
Create Date: 2026-04-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Drop login_tokens table if exists
    if "login_tokens" in inspector.get_table_names():
        op.drop_table("login_tokens")

    columns = [col["name"] for col in inspector.get_columns("users")]
    indexes = [idx["name"] for idx in inspector.get_indexes("users")]
    unique_constraints = [uc["name"] for uc in inspector.get_unique_constraints("users")]

    # Remove telegram-related columns (if they exist)
    if "ix_users_telegram_id" in indexes:
        op.drop_index("ix_users_telegram_id", table_name="users")
    if "uq_users_telegram_id" in unique_constraints:
        op.drop_constraint("uq_users_telegram_id", table_name="users", type_="unique")

    if "telegram_id" in columns:
        op.drop_column("users", "telegram_id")
    if "username" in columns:
        op.drop_column("users", "username")
    if "first_name" in columns:
        op.drop_column("users", "first_name")

    # Add new auth columns (if they don't exist)
    if "email" not in columns:
        op.add_column("users", sa.Column("email", sa.String(255), nullable=False, server_default=""))
    if "login" not in columns:
        op.add_column("users", sa.Column("login", sa.String(80), nullable=False, server_default=""))
    if "hashed_password" not in columns:
        op.add_column("users", sa.Column("hashed_password", sa.String(255), nullable=False, server_default=""))

    # Create unique indexes
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_unique_constraint("uq_users_login", "users", ["login"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_login", "users", ["login"])


def downgrade() -> None:
    op.drop_index("ix_users_login", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_constraint("uq_users_login", table_name="users", type_="unique")
    op.drop_constraint("uq_users_email", "users", type_="unique")

    op.drop_column("users", "hashed_password")
    op.drop_column("users", "login")
    op.drop_column("users", "email")

    op.add_column("users", sa.Column("first_name", sa.String(), nullable=False, server_default=""))
    op.add_column("users", sa.Column("username", sa.String(), nullable=True))
    op.add_column("users", sa.Column("telegram_id", sa.BigInteger(), nullable=False, server_default="0"))
    op.create_unique_constraint("uq_users_telegram_id", "users", ["telegram_id"])
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    op.create_table(
        "login_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
    )
