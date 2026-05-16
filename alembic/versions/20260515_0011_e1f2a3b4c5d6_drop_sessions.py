"""drop unused sessions table

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-05-15 00:02:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_sessions_user")
    op.execute("DROP INDEX IF EXISTS idx_sessions_token")
    op.drop_table("sessions")

def downgrade() -> None:
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
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("idx_sessions_token", "sessions", ["session_token"])
    op.create_index("idx_sessions_user", "sessions", ["user_id"])
