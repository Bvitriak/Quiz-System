import pytest

class TestPublishedImmutable:
    def test_update_basics_blocked(self, test_service, sample_test, db_session):
        with pytest.raises(ValueError, match="Unpublish"):
            test_service.update_basics(
                sample_test, title="x", time_limit_minutes=5,
                description="", randomize=False,
            )

    def test_add_question_blocked(self, test_service, sample_test):
        with pytest.raises(ValueError, match="Unpublish"):
            test_service.add_question(
                sample_test, qtype="single", text="?",
                options=["a", "b"], correct_indexes=[0],
            )

    def test_update_question_blocked(self, test_service, sample_test):
        question = sample_test.questions[0]
        with pytest.raises(ValueError, match="Unpublish"):
            test_service.update_question(
                question, text="x", options=["a", "b"], correct_indexes=[0],
            )

    def test_delete_question_blocked(self, test_service, sample_test):
        with pytest.raises(ValueError, match="Unpublish"):
            test_service.delete_question(sample_test, sample_test.questions[0].id)

    def test_update_availability_blocked(self, test_service, sample_test):
        with pytest.raises(ValueError, match="Unpublish"):
            test_service.update_availability(
                sample_test, start=None, end=None, max_attempts=2,
                show_result_immediately=True, randomize=False,
            )

    def test_to_draft_then_edit_works(self, test_service, sample_test, db_session):
        test_service.to_draft(sample_test)
        db_session.commit()
        test_service.update_basics(
            sample_test, title="new", time_limit_minutes=15,
            description="", randomize=False,
        )
        assert sample_test.title == "new"

class TestRegisterRace:
    def test_duplicate_email_raises_value_error(
        self, auth_service, role_repo, db_session,
    ):
        auth_service.register(
            email="dup@example.com", password="password123",
            full_name="A", role="student",
        )
        db_session.commit()
        with pytest.raises(ValueError, match="already exists"):
            auth_service.register(
                email="dup@example.com", password="password123",
                full_name="B", role="student",
            )

class TestAttemptUniqueness:
    def test_duplicate_attempt_no_blocked(
        self, quiz_service, sample_test, student, db_session,
    ):
        from sqlalchemy.exc import IntegrityError
        from src.models.result import TestAttempt
        from src.utils.time import utcnow

        db_session.add(TestAttempt(
            test_id=sample_test.id, student_id=student.id,
            attempt_no=1, started_at=utcnow(),
        ))
        db_session.commit()
        db_session.add(TestAttempt(
            test_id=sample_test.id, student_id=student.id,
            attempt_no=1, started_at=utcnow(),
        ))
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
