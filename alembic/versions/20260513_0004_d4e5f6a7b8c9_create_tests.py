"""create tests

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-13 00:03:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "tests",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "teacher_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", name="fk_tests_teacher_id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.String(255), nullable=False, server_default=""),
        sa.Column("time_limit_minutes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(255), nullable=False, server_default="draft"),
        sa.Column(
            "shuffle_questions",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("published_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_tests_teacher", "tests", ["teacher_id"])
    op.create_index("idx_tests_status", "tests", ["status"])

def downgrade() -> None:
    op.drop_index("idx_tests_status", table_name="tests")
    op.drop_index("idx_tests_teacher", table_name="tests")
    op.drop_table("tests")
