"""create roles

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-05-13 00:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("roles")
