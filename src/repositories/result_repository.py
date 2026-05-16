from sqlalchemy import func, select

from src.models.result import AttemptAnswer, AttemptAnswerOption, TestAttempt
from src.repositories.base_repository import BaseRepository


class TestAttemptRepository(BaseRepository[TestAttempt]):
    model = TestAttempt

    def list_for_user(self, user_id: int) -> list[TestAttempt]:
        stmt = (
            select(TestAttempt)
            .where(TestAttempt.student_id == user_id)
            .order_by(TestAttempt.started_at.desc())
        )
        return list(self.db.execute(stmt).scalars())

    def count_for_user_test(self, user_id: int, test_id: int) -> int:
        stmt = select(func.count(TestAttempt.id)).where(
            TestAttempt.student_id == user_id,
            TestAttempt.test_id == test_id,
        )
        return int(self.db.execute(stmt).scalar_one() or 0)

    def list_finished_for_users(
        self, user_ids: list[int]
    ) -> dict[int, list[TestAttempt]]:
        if not user_ids:
            return {}
        stmt = (
            select(TestAttempt)
            .where(
                TestAttempt.student_id.in_(user_ids),
                TestAttempt.finished_at.is_not(None),
            )
            .order_by(TestAttempt.finished_at.desc())
        )
        result: dict[int, list[TestAttempt]] = {uid: [] for uid in user_ids}
        for attempt in self.db.execute(stmt).scalars():
            result[attempt.student_id].append(attempt)
        return result

    def list_for_test(self, test_id: int) -> list[TestAttempt]:
        stmt = select(TestAttempt).where(TestAttempt.test_id == test_id)
        return list(self.db.execute(stmt).scalars())

    def count_active_for_test(self, test_id: int) -> int:
        stmt = select(func.count(TestAttempt.id)).where(
            TestAttempt.test_id == test_id,
            TestAttempt.finished_at.is_(None),
        )
        return int(self.db.execute(stmt).scalar_one() or 0)

class AttemptAnswerRepository(BaseRepository[AttemptAnswer]):
    model = AttemptAnswer

    def by_attempt_and_question(self, attempt_id: int, question_id: int) -> AttemptAnswer | None:
        stmt = select(AttemptAnswer).where(
            AttemptAnswer.attempt_id == attempt_id,
            AttemptAnswer.question_id == question_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

class AttemptAnswerOptionRepository(BaseRepository[AttemptAnswerOption]):
    model = AttemptAnswerOption
