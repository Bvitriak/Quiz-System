from datetime import datetime
from typing import Optional

from flask import g, redirect, url_for

from src.controllers.auth_controller import AuthController
from src.controllers.quiz_controller import QuizController
from src.controllers.test_controller import TestController
from src.repositories.result_repository import (
    AttemptAnswerOptionRepository,
    AttemptAnswerRepository,
    TestAttemptRepository,
)
from src.repositories.test_repository import (
    QuestionRepository,
    TestRepository,
)
from src.repositories.user_repository import RoleRepository, UserRepository
from src.services.auth_service import AuthService
from src.services.quiz_service import QuizService
from src.services.test_service import TestService


def auth_ctrl() -> AuthController:
    return AuthController(AuthService(UserRepository(g.db), RoleRepository(g.db)))

def quiz_ctrl() -> QuizController:
    return QuizController(QuizService(
        TestRepository(g.db),
        TestAttemptRepository(g.db),
        AttemptAnswerRepository(g.db),
        AttemptAnswerOptionRepository(g.db),
    ))

def test_ctrl() -> TestController:
    return TestController(TestService(
        TestRepository(g.db),
        QuestionRepository(g.db),
        TestAttemptRepository(g.db),
    ))

def parse_dt(date_s: str, time_s: str) -> Optional[datetime]:
    date_s = (date_s or "").strip()
    time_s = (time_s or "").strip()
    if not date_s:
        return None
    try:
        return datetime.fromisoformat(date_s + "T" + (time_s or "00:00"))
    except ValueError:
        return None

def format_duration(seconds: int) -> str:
    minutes, secs = divmod(max(0, seconds or 0), 60)
    return f"{minutes} min {secs} s"

def feedback_for(
    percent: int, pass_threshold: int, excellent_threshold: int = 80,
) -> str:
    if percent >= excellent_threshold:
        return "Excellent result! You demonstrated deep knowledge."
    if percent >= pass_threshold:
        return "Good result. There is still room to improve."
    return "Worth reviewing the material and trying again."

def redirect_for_role(user):
    return redirect(url_for("teacher.index" if user.is_teacher else "student.index"))
