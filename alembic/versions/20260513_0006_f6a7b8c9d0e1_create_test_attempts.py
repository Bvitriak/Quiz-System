"""create test_attempts, attempt_answers, attempt_answer_options

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-05-13 00:05:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "test_attempts",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "test_id",
            sa.BigInteger(),
            sa.ForeignKey("tests.id", name="fk_test_attempts_test_id"),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", name="fk_test_attempts_student_id"),
            nullable=False,
        ),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(255),
            nullable=False,
            server_default="in_progress",
        ),
        sa.Column(
            "started_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column(
            "time_spent_seconds",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "success_percent",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "correct_answers_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_index("idx_attempts_student", "test_attempts", ["student_id"])
    op.create_index("idx_attempts_test", "test_attempts", ["test_id"])

    op.create_table(
        "attempt_answers",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "attempt_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "test_attempts.id",
                name="fk_attempt_answers_attempt_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "questions.id",
                name="fk_attempt_answers_question_id",
            ),
            nullable=False,
        ),
        sa.Column(
            "question_order_shown",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "text_answer_raw",
            sa.String(255),
            nullable=False,
            server_default="",
        ),
        sa.Column(
            "text_answer_normalized",
            sa.String(255),
            nullable=False,
            server_default="",
        ),
        sa.Column(
            "is_correct",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "awarded_points",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_index("idx_answers_attempt", "attempt_answers", ["attempt_id"])

    op.create_table(
        "attempt_answer_options",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "attempt_answer_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "attempt_answers.id",
                name="fk_attempt_answer_options_answer_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "option_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "question_options.id",
                name="fk_attempt_answer_options_option_id",
            ),
            nullable=False,
        ),
        sa.Column(
            "option_order_shown",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_index(
        "idx_answer_opts_answer", "attempt_answer_options", ["attempt_answer_id"]
    )

def downgrade() -> None:
    op.drop_index("idx_answer_opts_answer", table_name="attempt_answer_options")
    op.drop_table("attempt_answer_options")
    op.drop_index("idx_answers_attempt", table_name="attempt_answers")
    op.drop_table("attempt_answers")
    op.drop_index("idx_attempts_test", table_name="test_attempts")
    op.drop_index("idx_attempts_student", table_name="test_attempts")
    op.drop_table("test_attempts")
