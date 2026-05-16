"""cascade delete for test_attempts.test_id and attempt_answers.question_id

Revision ID: a3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-05-16 00:00:00
"""
from typing import Sequence, Union

from alembic import op

revision: str = "a3b4c5d6e7f8"
down_revision: Union[str, None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table("test_attempts") as batch_op:
        batch_op.drop_constraint("fk_test_attempts_test_id", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_test_attempts_test_id",
            "tests",
            ["test_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_unique_constraint(
            "uq_test_attempts_student_attempt",
            ["test_id", "student_id", "attempt_no"],
        )

    with op.batch_alter_table("attempt_answers") as batch_op:
        batch_op.drop_constraint("fk_attempt_answers_question_id", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_attempt_answers_question_id",
            "questions",
            ["question_id"],
            ["id"],
            ondelete="CASCADE",
        )

def downgrade() -> None:
    with op.batch_alter_table("attempt_answers") as batch_op:
        batch_op.drop_constraint("fk_attempt_answers_question_id", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_attempt_answers_question_id",
            "questions",
            ["question_id"],
            ["id"],
        )

    with op.batch_alter_table("test_attempts") as batch_op:
        batch_op.drop_constraint(
            "uq_test_attempts_student_attempt", type_="unique"
        )
        batch_op.drop_constraint("fk_test_attempts_test_id", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_test_attempts_test_id",
            "tests",
            ["test_id"],
            ["id"],
        )
