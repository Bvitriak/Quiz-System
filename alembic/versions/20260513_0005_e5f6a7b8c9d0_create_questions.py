"""create questions, question_options, question_text_answers

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-13 00:04:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "test_id",
            sa.BigInteger(),
            sa.ForeignKey("tests.id", name="fk_questions_test_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_type", sa.String(255), nullable=False),
        sa.Column("text", sa.String(255), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("idx_questions_test", "questions", ["test_id"])

    op.create_table(
        "question_options",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "question_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "questions.id",
                name="fk_question_options_question_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("option_text", sa.String(255), nullable=False),
        sa.Column(
            "is_correct",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("idx_options_question", "question_options", ["question_id"])

    op.create_table(
        "question_text_answers",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "question_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "questions.id",
                name="fk_question_text_answers_question_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("accepted_answer", sa.String(255), nullable=False),
        sa.Column("normalized_answer", sa.String(255), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("question_text_answers")
    op.drop_index("idx_options_question", table_name="question_options")
    op.drop_table("question_options")
    op.drop_index("idx_questions_test", table_name="questions")
    op.drop_table("questions")
