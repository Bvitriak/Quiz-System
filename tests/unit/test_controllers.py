from unittest.mock import MagicMock
import pytest
from src.controllers.auth_controller import AuthController
from src.controllers.quiz_controller import QuizController
from src.controllers.test_controller import TestController

class TestAuthController:
    def test_login_normalizes_email_and_calls_service(self):
        service = MagicMock()
        controller = AuthController(service)
        controller.login("  Foo@X.IO ", "password123")
        service.login.assert_called_once_with("foo@x.io", "password123")

    def test_login_short_password_raises(self):
        controller = AuthController(MagicMock())
        with pytest.raises(ValueError):
            controller.login("a@b.io", "12")

    def test_register_password_mismatch(self):
        controller = AuthController(MagicMock())
        with pytest.raises(ValueError, match="do not match"):
            controller.register("a@b.io", "secret123", "secret999", "Anna", "student")

    def test_register_empty_name(self):
        controller = AuthController(MagicMock())
        with pytest.raises(ValueError, match="Name"):
            controller.register("a@b.io", "secret123", "secret123", "  ", "student")

    def test_register_invalid_role(self):
        controller = AuthController(MagicMock())
        with pytest.raises(ValueError):
            controller.register("a@b.io", "secret123", "secret123", "Anna", "admin")

    def test_register_ok_delegates(self):
        service = MagicMock()
        controller = AuthController(service)
        controller.register("a@b.io", "secret123", "secret123", "Anna", "STUDENT")
        service.register.assert_called_once_with(
            "a@b.io", "secret123", "Anna", "student"
        )

    def test_logout_delegates(self):
        service = MagicMock()
        AuthController(service).logout()
        service.logout.assert_called_once()

class TestQuizController:
    def test_methods_delegate(self):
        service = MagicMock()
        controller = QuizController(service)

        controller.list_tests()
        service.list_tests.assert_called_once()

        controller.history_for(7)
        service.history_for.assert_called_with(7)

        controller.start_attempt(7, 3)
        service.start_attempt.assert_called_with(7, 3)

        controller.attempts_used(7, 3)
        service.attempts_used.assert_called_with(7, 3)

        controller.last_attempt(7, 3)
        service.last_attempt.assert_called_with(7, 3)

        attempt = MagicMock()
        controller.remaining_seconds(attempt)
        service.remaining_seconds.assert_called_with(attempt)

        question = MagicMock()
        controller.save_answer(attempt, question, 2)
        service.save_answer.assert_called_with(attempt, question, 2)

        controller.save_text_answer(attempt, question, "hello")
        service.save_text_answer.assert_called_with(attempt, question, "hello")

class TestTestController:
    def test_delegations(self):
        service = MagicMock()
        controller = TestController(service)

        controller.list_for_owner(1)
        service.list_for_owner.assert_called_with(1)

        controller.create(
            owner_id=1, title="t", time_limit_minutes=10,
            description="d", randomize=False,
        )
        service.create.assert_called_once()

        test_obj = MagicMock()
        controller.update_basics(
            test_obj, title="t", time_limit_minutes=10,
            description="d", randomize=True,
        )
        service.update_basics.assert_called_once()

        controller.publish(test_obj)
        service.publish.assert_called_with(test_obj, changed_by=None)

        controller.to_draft(test_obj)
        service.to_draft.assert_called_with(test_obj, changed_by=None)

        question = MagicMock()
        controller.update_question(
            question, text="x", options=[], correct_indexes=[], correct_text="",
        )
        service.update_question.assert_called_once()

        controller.delete_question(test_obj, 5)
        service.delete_question.assert_called_with(test_obj, 5)
