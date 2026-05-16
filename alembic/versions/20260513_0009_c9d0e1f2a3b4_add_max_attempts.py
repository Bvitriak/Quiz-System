"""add tests.max_attempts column

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-05-13 00:08:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        "tests",
        sa.Column("max_attempts", sa.Integer(), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("tests", "max_attempts")
