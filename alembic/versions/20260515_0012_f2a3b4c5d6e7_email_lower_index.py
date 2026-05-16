"""enforce case-insensitive uniqueness on users.email

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-05-15 00:03:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_index(
        "ix_users_email_lower",
        "users",
        [sa.text("LOWER(email)")],
        unique=True,
    )

def downgrade() -> None:
    op.drop_index("ix_users_email_lower", table_name="users")
