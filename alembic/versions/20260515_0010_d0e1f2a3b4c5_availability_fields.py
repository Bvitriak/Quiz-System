"""add availability fields and convert description to text

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-05-15 00:01:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: Union[str, None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        "tests",
        sa.Column("availability_start", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "tests",
        sa.Column("availability_end", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "tests",
        sa.Column(
            "show_result_immediately",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.alter_column(
        "tests",
        "description",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=False,
        nullable=True,
        existing_server_default="",
        server_default=None,
    )

def downgrade() -> None:
    op.alter_column(
        "tests",
        "description",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=True,
        nullable=False,
        server_default="",
    )
    op.drop_column("tests", "show_result_immediately")
    op.drop_column("tests", "availability_end")
    op.drop_column("tests", "availability_start")
