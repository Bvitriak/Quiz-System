"""create sessions

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-13 00:02:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", name="fk_sessions_user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("session_token", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("idx_sessions_token", "sessions", ["session_token"])
    op.create_index("idx_sessions_user", "sessions", ["user_id"])

def downgrade() -> None:
    op.drop_index("idx_sessions_user", table_name="sessions")
    op.drop_index("idx_sessions_token", table_name="sessions")
    op.drop_table("sessions")
