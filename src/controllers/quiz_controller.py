from typing import Optional

from src.models.question import Question
from src.models.result import TestAttempt
from src.models.test import Test
from src.services.quiz_service import QuizService


class QuizController:

    def __init__(self, quiz_service: QuizService) -> None:
        self._quiz = quiz_service

    def list_tests(self) -> list[Test]:
        return self._quiz.list_tests()

    def history_for(self, user_id: int) -> list[TestAttempt]:
        return self._quiz.history_for(user_id)

    def start_attempt(self, user_id: int, test_id: int) -> TestAttempt:
        return self._quiz.start_attempt(user_id, test_id)

    def attempts_used(self, user_id: int, test_id: int) -> int:
        return self._quiz.attempts_used(user_id, test_id)

    def can_start(self, user_id: int, test: Test) -> bool:
        return self._quiz.can_start(user_id, test)

    def can_view_result(self, test: Test) -> bool:
        return self._quiz.can_view_result(test)

    def last_attempt(self, user_id: int, test_id: int) -> Optional[TestAttempt]:
        return self._quiz.last_attempt(user_id, test_id)

    def get_attempt(self, attempt_id: int) -> Optional[TestAttempt]:
        return self._quiz.get_attempt(attempt_id)

    def get_test(self, test_id: int) -> Optional[Test]:
        return self._quiz.get_test(test_id)

    def remaining_seconds(self, attempt: TestAttempt) -> int:
        return self._quiz.remaining_seconds(attempt)

    def ordered_questions(self, attempt: TestAttempt, test: Test) -> list[Question]:
        return self._quiz.ordered_questions(attempt, test)

    def save_answer(
        self, attempt: TestAttempt, question: Question, option_index: int,
    ) -> None:
        self._quiz.save_answer(attempt, question, option_index)

    def save_multi_answer(
        self, attempt: TestAttempt, question: Question, option_indexes: list[int],
    ) -> None:
        self._quiz.save_multi_answer(attempt, question, option_indexes)

    def save_text_answer(
        self, attempt: TestAttempt, question: Question, text: str,
    ) -> None:
        self._quiz.save_text_answer(attempt, question, text)

    def finish_attempt(self, attempt: TestAttempt) -> TestAttempt:
        return self._quiz.finish_attempt(attempt)
