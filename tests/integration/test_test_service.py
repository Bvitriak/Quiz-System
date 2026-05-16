import pytest

class TestCreate:
    def test_ok(self, test_service, teacher, db_session):
        test_obj = test_service.create(
            owner_id=teacher.id, title="A",
            time_limit_minutes=20, description="d", randomize=True,
        )
        db_session.commit()
        assert test_obj.id is not None
        assert test_obj.title == "A"
        assert test_obj.shuffle_questions is True

    def test_empty_title(self, test_service, teacher):
        with pytest.raises(ValueError):
            test_service.create(
                owner_id=teacher.id, title="   ",
                time_limit_minutes=10, description="", randomize=False,
            )

    def test_bad_time_limit(self, test_service, teacher):
        with pytest.raises(ValueError):
            test_service.create(
                owner_id=teacher.id, title="A",
                time_limit_minutes=0, description="", randomize=False,
            )

class TestQuestions:
    def test_single_requires_one_correct(
        self, test_service, teacher, db_session
    ):
        test_obj = test_service.create(
            owner_id=teacher.id, title="A",
            time_limit_minutes=10, description="", randomize=False,
        )
        with pytest.raises(ValueError, match="one correct"):
            test_service.add_question(
                test_obj, qtype="single", text="?",
                options=["a", "b"], correct_indexes=[0, 1],
            )

    def test_choice_requires_two_options(self, test_service, teacher):
        test_obj = test_service.create(
            owner_id=teacher.id, title="A",
            time_limit_minutes=10, description="", randomize=False,
        )
        with pytest.raises(ValueError, match="at least two"):
            test_service.add_question(
                test_obj, qtype="single", text="?",
                options=["a"], correct_indexes=[0],
            )

    def test_choice_must_mark_correct(self, test_service, teacher):
        test_obj = test_service.create(
            owner_id=teacher.id, title="A",
            time_limit_minutes=10, description="", randomize=False,
        )
        with pytest.raises(ValueError, match="correct"):
            test_service.add_question(
                test_obj, qtype="single", text="?",
                options=["a", "b"], correct_indexes=[],
            )

    def test_unknown_type(self, test_service, teacher):
        test_obj = test_service.create(
            owner_id=teacher.id, title="A",
            time_limit_minutes=10, description="", randomize=False,
        )
        with pytest.raises(ValueError):
            test_service.add_question(
                test_obj, qtype="weird", text="?", options=[], correct_indexes=[],
            )

    def test_update_and_delete(
        self, test_service, sample_test, db_session
    ):
        test_service.to_draft(sample_test)
        db_session.commit()

        question = sample_test.questions[0]
        test_service.update_question(
            question, text="new",
            options=["a", "b", "c"], correct_indexes=[2], correct_text="",
        )
        db_session.commit()
        assert question.text == "new"
        assert question.correct_indexes == [2]

        question_id = question.id
        test_service.delete_question(sample_test, question_id)
        db_session.commit()
        assert all(other.id != question_id for other in sample_test.questions)

class TestPublish:
    def test_publish_requires_questions(self, test_service, teacher, db_session):
        test_obj = test_service.create(
            owner_id=teacher.id, title="Empty",
            time_limit_minutes=10, description="", randomize=False,
        )
        with pytest.raises(ValueError):
            test_service.publish(test_obj)

    def test_publish_sets_status(self, test_service, sample_test, db_session):
        test_service.to_draft(sample_test)
        db_session.commit()
        assert not sample_test.is_published
        test_service.publish(sample_test)
        assert sample_test.is_published
        assert sample_test.published_at is not None

class TestStatusHistoryRecording:
    def test_publish_writes_history(self, test_service, sample_test, db_session, teacher):
        test_service.to_draft(sample_test, changed_by=teacher.id)
        test_service.publish(sample_test, changed_by=teacher.id)
        db_session.commit()

        from src.models.test import TestStatusHistory
        rows = db_session.query(TestStatusHistory).filter_by(test_id=sample_test.id).all()
        assert any(row.new_status == "draft" for row in rows)
        assert any(row.new_status == "published" for row in rows)

    def test_no_history_when_same_status(self, test_service, sample_test, db_session, teacher):
        from src.models.test import TestStatusHistory
        before = db_session.query(TestStatusHistory).count()
        test_service.publish(sample_test, changed_by=teacher.id)
        db_session.commit()
        after = db_session.query(TestStatusHistory).count()
        assert before == after

class TestPointsAndTextAnswer:
    def test_non_integer_points_rejected(self, test_service, teacher):
        test_obj = test_service.create(
            owner_id=teacher.id, title="P",
            time_limit_minutes=10, description="", randomize=False,
        )
        import pytest
        with pytest.raises(ValueError, match="[Ss]core"):
            test_service.add_question(
                test_obj, qtype="single", text="?",
                options=["a", "b"], correct_indexes=[0],
                points="abc",
            )

    def test_text_answer_stored_normalized(self, test_service, teacher, db_session):
        test_obj = test_service.create(
            owner_id=teacher.id, title="T",
            time_limit_minutes=10, description="", randomize=False,
        )
        question = test_service.add_question(
            test_obj, qtype="text", text="?",
            options=[], correct_indexes=[],
            correct_text="  Paris  ",
        )
        db_session.commit()
        assert question.text_answers[0].accepted_answer == "Paris"
        assert question.text_answers[0].normalized_answer == "paris"

    def test_update_question_replaces_text_answer(self, test_service, teacher, db_session):
        test_obj = test_service.create(
            owner_id=teacher.id, title="T",
            time_limit_minutes=10, description="", randomize=False,
        )
        question = test_service.add_question(
            test_obj, qtype="text", text="?",
            options=[], correct_indexes=[],
            correct_text="old",
        )
        test_service.update_question(
            question, text="new",
            options=[], correct_indexes=[],
            correct_text="new",
        )
        db_session.commit()
        assert len(question.text_answers) == 1
        assert question.text_answers[0].accepted_answer == "new"

class TestStudentStats:
    def test_stats_aggregates(self, test_service, quiz_service, sample_test, student, db_session):
        attempt = quiz_service.start_attempt(student.id, sample_test.id)
        quiz_service.save_answer(attempt, sample_test.questions[0], 1)
        quiz_service.finish_attempt(attempt)
        db_session.commit()

        rows = test_service.student_stats([student])
        assert rows[0]["student"] is student
        assert rows[0]["attempts_count"] == 1
        assert rows[0]["last_attempt"].id == attempt.id
