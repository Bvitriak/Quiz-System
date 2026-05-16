from datetime import datetime, timedelta

import pytest

def make_text_test(test_service, teacher, expected: str = ""):
    test_obj = test_service.create(
        owner_id=teacher.id, title="Text",
        time_limit_minutes=10, description="", randomize=False,
    )
    test_service.add_question(
        test_obj, qtype="text", text="Capital of France?",
        options=[], correct_indexes=[],
        correct_text=expected, points=1,
    )
    test_service.publish(test_obj)
    return test_obj

class TestTextAnswerMatching:
    def test_no_expected_any_non_empty_is_correct(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = make_text_test(test_service, teacher, expected="")
        db_session.commit()

        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        quiz_service.save_text_answer(attempt, test_obj.questions[0], "something")
        quiz_service.finish_attempt(attempt)
        assert attempt.correct_count == 1

    def test_with_expected_exact_match_correct(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = make_text_test(test_service, teacher, expected="Paris")
        db_session.commit()

        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        quiz_service.save_text_answer(attempt, test_obj.questions[0], "Paris")
        quiz_service.finish_attempt(attempt)
        assert attempt.correct_count == 1

    def test_with_expected_case_and_whitespace_insensitive(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = make_text_test(test_service, teacher, expected="Paris")
        db_session.commit()

        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        quiz_service.save_text_answer(attempt, test_obj.questions[0], "  paris  ")
        quiz_service.finish_attempt(attempt)
        assert attempt.correct_count == 1

    def test_with_expected_wrong_answer_marked_incorrect(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = make_text_test(test_service, teacher, expected="Paris")
        db_session.commit()

        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        quiz_service.save_text_answer(attempt, test_obj.questions[0], "London")
        quiz_service.finish_attempt(attempt)
        assert attempt.correct_count == 0

class TestMultipleChoicePartialScoring:
    def build(self, test_service, teacher, db_session, points: int = 4):
        test_obj = test_service.create(
            owner_id=teacher.id, title="Even",
            time_limit_minutes=10, description="", randomize=False,
        )
        test_service.add_question(
            test_obj, qtype="multiple", text="Select even numbers",
            options=["1", "2", "3", "4"], correct_indexes=[1, 3],
            points=points,
        )
        test_service.publish(test_obj)
        db_session.commit()
        return test_obj

    def test_full_match_full_points(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = self.build(test_service, teacher, db_session, points=4)
        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        question = test_obj.questions[0]
        quiz_service.save_multi_answer(attempt, question, [1, 3])
        quiz_service.finish_attempt(attempt)
        assert attempt.score == 4
        assert attempt.correct_count == 1

    def test_one_of_two_correct_gives_half(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = self.build(test_service, teacher, db_session, points=4)
        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        question = test_obj.questions[0]
        quiz_service.save_multi_answer(attempt, question, [1])
        quiz_service.finish_attempt(attempt)
        assert attempt.score == 2
        assert attempt.correct_count == 0

    def test_one_correct_one_wrong_zero(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = self.build(test_service, teacher, db_session, points=4)
        attempt = quiz_service.start_attempt(student.id, test_obj.id)
        question = test_obj.questions[0]
        quiz_service.save_multi_answer(attempt, question, [1, 0])
        quiz_service.finish_attempt(attempt)
        assert attempt.score == 0
        assert attempt.correct_count == 0

class TestSchedule:
    def test_within_window_can_start(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = test_service.create(
            owner_id=teacher.id, title="Window",
            time_limit_minutes=5, description="", randomize=False,
        )
        test_service.add_question(
            test_obj, qtype="single", text="?",
            options=["a", "b"], correct_indexes=[0],
        )
        test_service.publish(test_obj)
        test_obj.availability_start = datetime.utcnow() - timedelta(hours=1)
        test_obj.availability_end = datetime.utcnow() + timedelta(hours=1)
        db_session.commit()
        assert quiz_service.can_start(student.id, test_obj) is True

    def test_before_start_blocked(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = test_service.create(
            owner_id=teacher.id, title="Future",
            time_limit_minutes=5, description="", randomize=False,
        )
        test_service.add_question(
            test_obj, qtype="single", text="?",
            options=["a", "b"], correct_indexes=[0],
        )
        test_service.publish(test_obj)
        test_obj.availability_start = datetime.utcnow() + timedelta(hours=1)
        db_session.commit()
        assert quiz_service.can_start(student.id, test_obj) is False
        with pytest.raises(ValueError, match="not available"):
            quiz_service.start_attempt(student.id, test_obj.id)

    def test_after_end_blocked(
        self, test_service, quiz_service, teacher, student, db_session
    ):
        test_obj = test_service.create(
            owner_id=teacher.id, title="Past",
            time_limit_minutes=5, description="", randomize=False,
        )
        test_service.add_question(
            test_obj, qtype="single", text="?",
            options=["a", "b"], correct_indexes=[0],
        )
        test_service.publish(test_obj)
        test_obj.availability_end = datetime.utcnow() - timedelta(minutes=1)
        db_session.commit()
        assert quiz_service.can_start(student.id, test_obj) is False

class TestPointsValidation:
    def test_zero_points_rejected(self, test_service, teacher, db_session):
        test_obj = test_service.create(
            owner_id=teacher.id, title="P",
            time_limit_minutes=10, description="", randomize=False,
        )
        with pytest.raises(ValueError, match="[Ss]core"):
            test_service.add_question(
                test_obj, qtype="single", text="?",
                options=["a", "b"], correct_indexes=[0],
                points=0,
            )

    def test_custom_points_persisted(self, test_service, teacher, db_session):
        test_obj = test_service.create(
            owner_id=teacher.id, title="P",
            time_limit_minutes=10, description="", randomize=False,
        )
        question = test_service.add_question(
            test_obj, qtype="single", text="?",
            options=["a", "b"], correct_indexes=[0],
            points=5,
        )
        db_session.commit()
        assert question.points == 5
