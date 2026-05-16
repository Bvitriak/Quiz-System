import pytest
from src.models.user import Role

class TestRoleRepository:
    def test_ensure_default_creates_roles(self, role_repo):
        assert role_repo.by_code("student") is not None
        assert role_repo.by_code("teacher") is not None

    def test_ensure_default_idempotent(self, role_repo, db_session):
        role_repo.ensure_default()
        db_session.commit()
        count = db_session.query(Role).count()
        assert count == 2

class TestUserRepository:
    def test_by_email_returns_none_when_missing(self, user_repo):
        assert user_repo.by_email("noone@example.com") is None

    def test_create_and_lookup(self, user_repo, role_repo, db_session):
        from src.models.user import User
        student_role = role_repo.by_code("student")
        new_user = User(
            role_id=student_role.id,
            email="x@y.io",
            password_hash="hash",
            full_name="X",
        )
        user_repo.add(new_user)
        db_session.commit()
        assert user_repo.by_email("x@y.io").full_name == "X"
        assert user_repo.list_by_role_code("student")[0].email == "x@y.io"


class TestTestRepository:
    def test_list_published_filters_drafts(self, test_repo, sample_test, db_session):
        from src.models.test import STATUS_DRAFT, Test
        draft = Test(
            teacher_id=sample_test.teacher_id,
            title="Draft",
            time_limit_minutes=15,
            status=STATUS_DRAFT,
        )
        test_repo.add(draft)
        db_session.commit()

        published = test_repo.list_published()
        ids = {test_obj.id for test_obj in published}
        assert sample_test.id in ids
        assert draft.id not in ids

    def test_list_for_owner(self, test_repo, sample_test, teacher):
        owned = test_repo.list_for_owner(teacher.id)
        assert any(test_obj.id == sample_test.id for test_obj in owned)

class TestAttemptRepository:
    def test_count_and_list(self, quiz_service, sample_test, student, db_session):
        first_attempt = quiz_service.start_attempt(student.id, sample_test.id)
        quiz_service.finish_attempt(first_attempt)
        second_attempt = quiz_service.start_attempt(student.id, sample_test.id)
        quiz_service.finish_attempt(second_attempt)
        db_session.commit()

        history = quiz_service.history_for(student.id)
        assert len(history) == 2
        assert history[0].started_at >= history[1].started_at

@pytest.mark.parametrize("missing_id", [0, 999, -1])
def test_get_returns_none_for_missing(test_repo, missing_id):
    assert test_repo.get(missing_id) is None
