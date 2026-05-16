"""create test_status_history

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-05-13 00:06:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "test_status_history",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "test_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "tests.id",
                name="fk_test_status_history_test_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "changed_by",
            sa.BigInteger(),
            sa.ForeignKey("users.id", name="fk_test_status_history_changed_by"),
            nullable=False,
        ),
        sa.Column("old_status", sa.String(255), nullable=False),
        sa.Column("new_status", sa.String(255), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("idx_status_history_test", "test_status_history", ["test_id"])

def downgrade() -> None:
    op.drop_index("idx_status_history_test", table_name="test_status_history")
    op.drop_table("test_status_history")
