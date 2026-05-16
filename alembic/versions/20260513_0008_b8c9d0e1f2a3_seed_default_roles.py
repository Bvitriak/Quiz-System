"""seed default roles (student, teacher)

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-05-13 00:07:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

roles_table = sa.table(
    "roles",
    sa.column("code", sa.String),
    sa.column("name", sa.String),
)

def upgrade() -> None:
    op.bulk_insert(
        roles_table,
        [
            {"code": "student", "name": "Student"},
            {"code": "teacher", "name": "Teacher"},
        ],
    )

def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE code IN ('student', 'teacher')")
