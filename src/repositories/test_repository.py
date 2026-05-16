from typing import Optional

from sqlalchemy import select

from src.models.question import Question, QuestionOption, QuestionTextAnswer
from src.models.test import STATUS_PUBLISHED, Test, TestStatusHistory
from src.repositories.base_repository import BaseRepository


class TestRepository(BaseRepository[Test]):
    model = Test

    def list_published(self) -> list[Test]:
        stmt = (
            select(Test)
            .where(Test.status == STATUS_PUBLISHED)
            .order_by(Test.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars())

    def list_for_owner(self, owner_id: int) -> list[Test]:
        stmt = (
            select(Test)
            .where(Test.teacher_id == owner_id)
            .order_by(Test.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars())

    def add_status_history(self, entry: TestStatusHistory) -> TestStatusHistory:
        self.db.add(entry)
        self.db.flush()
        return entry

class QuestionRepository(BaseRepository[Question]):
    model = Question

    def next_position(self, test_id: int) -> int:
        stmt = select(Question).where(Question.test_id == test_id)
        rows = list(self.db.execute(stmt).scalars())
        return (max((q.position for q in rows), default=-1)) + 1

class QuestionOptionRepository(BaseRepository[QuestionOption]):
    model = QuestionOption

    def by_id(self, option_id: int) -> Optional[QuestionOption]:
        return self.get(option_id)

class QuestionTextAnswerRepository(BaseRepository[QuestionTextAnswer]):
    model = QuestionTextAnswer
