import pytest

class TestStartAttempt:
    def test_creates_attempt_with_number_1(self, quiz_service, sample_test, student):
        attempt = quiz_service.start_attempt(student.id, sample_test.id)
        assert attempt.attempt_no == 1
        assert attempt.student_id == student.id
        assert attempt.test_id == sample_test.id
        assert not attempt.is_finished

    def test_second_attempt_increments(self, quiz_service, sample_test, student, db_session):
        first_attempt = quiz_service.start_attempt(student.id, sample_test.id)
        quiz_service.finish_attempt(first_attempt)
        db_session.commit()
        second_attempt = quiz_service.start_attempt(student.id, sample_test.id)
        assert second_attempt.attempt_no == 2

    def test_unknown_test_raises(self, quiz_service, student):
        with pytest.raises(ValueError):
            quiz_service.start_attempt(student.id, 99999)

    def test_blocked_when_limit_reached(self, quiz_service, sample_test, student, db_session):
        sample_test.max_attempts = 1
        db_session.commit()
        first = quiz_service.start_attempt(student.id, sample_test.id)
        quiz_service.finish_attempt(first)
        db_session.commit()
        with pytest.raises(ValueError, match="[Ll]imit"):
            quiz_service.start_attempt(student.id, sample_test.id)

class TestSaveAnswer:
    def test_single_choice_correct(
        self, quiz_service, sample_test, student, db_session
    ):
        attempt = quiz_service.start_attempt(student.id, sample_test.id)
        question = sample_test.questions[0]
        quiz_service.save_answer(attempt, question, 1)
        db_session.commit()

        attempt = quiz_service.finish_attempt(attempt)
        db_session.commit()
        assert attempt.correct_count == 1
        assert attempt.success_percent > 0

    def test_single_choice_wrong(
        self, quiz_service, sample_test, student, db_session
    ):
        attempt = quiz_service.start_attempt(student.id, sample_test.id)
        quiz_service.save_answer(attempt, sample_test.questions[0], 0)
        db_session.commit()
        quiz_service.finish_attempt(attempt)
        assert attempt.correct_count == 0

    def test_no_op_when_attempt_finished(
        self, quiz_service, sample_test, student, db_session
    ):
        attempt = quiz_service.start_attempt(student.id, sample_test.id)
        quiz_service.finish_attempt(attempt)
        db_session.commit()
        quiz_service.save_answer(attempt, sample_test.questions[0], 1)
        assert attempt.correct_count == 0

class TestTextAnswer:
    def test_text_answer_correct_when_non_empty(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = test_service.create(
            owner_id=teacher.id, title="Text",
            time_limit_minutes=10, description="", randomize=False,
        )
        test_service.add_question(
            test_obj, qtype="text", text="Describe the algorithm",
            options=[], correct_indexes=[],
        )
        test_service.publish(test_obj)
        db_session.commit()

        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        quiz_service.save_text_answer(attempt, test_obj.questions[0], "First ...")
        quiz_service.finish_attempt(attempt)
        db_session.commit()

        assert attempt.correct_count == 1

    def test_text_answer_empty_marked_wrong(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = test_service.create(
            owner_id=teacher.id, title="T",
            time_limit_minutes=10, description="", randomize=False,
        )
        test_service.add_question(
            test_obj, qtype="text", text="?", options=[], correct_indexes=[],
        )
        test_service.publish(test_obj)
        db_session.commit()

        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        quiz_service.save_text_answer(attempt, test_obj.questions[0], "   ")
        quiz_service.finish_attempt(attempt)
        assert attempt.correct_count == 0

class TestRemainingSeconds:
    def test_returns_positive_for_fresh(self, quiz_service, sample_test, student):
        attempt = quiz_service.start_attempt(student.id, sample_test.id)
        assert quiz_service.remaining_seconds(attempt) > 0

class TestCanStart:
    def test_unlimited(self, quiz_service, sample_test, student):
        sample_test.max_attempts = None
        assert quiz_service.can_start(student.id, sample_test) is True

    def test_blocked(self, quiz_service, sample_test, student, db_session):
        sample_test.max_attempts = 1
        db_session.commit()
        attempt = quiz_service.start_attempt(student.id, sample_test.id)
        quiz_service.finish_attempt(attempt)
        db_session.commit()
        assert quiz_service.can_start(student.id, sample_test) is False
