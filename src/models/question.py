from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.test import Test

TYPE_SINGLE = "single"
TYPE_MULTIPLE = "multiple"
TYPE_TEXT = "text"

_TYPE_LABELS = {
    TYPE_SINGLE: "Single choice",
    TYPE_MULTIPLE: "Multiple choice",
    TYPE_TEXT: "Text answer",
}

class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    question_type: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    test: Mapped["Test"] = relationship("Test", back_populates="questions")
    options: Mapped[list["QuestionOption"]] = relationship(
        "QuestionOption",
        back_populates="question",
        order_by="QuestionOption.position",
        cascade="all, delete-orphan",
    )
    text_answers: Mapped[list["QuestionTextAnswer"]] = relationship(
        "QuestionTextAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    @property
    def type(self) -> str:
        return self.question_type

    @property
    def type_label(self) -> str:
        return _TYPE_LABELS.get(self.question_type, self.question_type)

    @property
    def option_texts(self) -> list[str]:
        return [o.option_text for o in self.options]

    @property
    def correct_indexes(self) -> list[int]:
        return [i for i, o in enumerate(self.options) if o.is_correct]

    @property
    def correct_index(self) -> int:
        idx = self.correct_indexes
        return idx[0] if idx else 0

    @property
    def correct_text(self) -> str:
        return self.text_answers[0].accepted_answer if self.text_answers else ""

class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(String(255), nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    question: Mapped["Question"] = relationship("Question", back_populates="options")

class QuestionTextAnswer(Base):
    __tablename__ = "question_text_answers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    accepted_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_answer: Mapped[str] = mapped_column(String(255), nullable=False)

    question: Mapped["Question"] = relationship("Question", back_populates="text_answers")
