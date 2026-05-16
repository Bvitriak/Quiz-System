from __future__ import annotations
import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["APP_SECRET_KEY"] = "test-secret"
os.environ["DEBUG"] = "false"

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest  # noqa: E402
from sqlalchemy import BigInteger, create_engine, event  # noqa: E402
from sqlalchemy.ext.compiler import compiles  # noqa: E402
from sqlalchemy.orm import scoped_session, sessionmaker  # noqa: E402

@compiles(BigInteger, "sqlite")
def _bigint_as_integer(element, compiler, **kw):  # pragma: no cover
    return "INTEGER"


def _enable_fk(dbapi_conn, _):  # pragma: no cover
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

from src.models.base import Base  # noqa: E402
from src.models import question  # noqa: E402,F401
from src.models import result  # noqa: E402,F401
from src.models import test  # noqa: E402,F401
from src.models import user  # noqa: E402,F401

@pytest.fixture(scope="session")
def engine():
    sqlite_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    event.listen(sqlite_engine, "connect", _enable_fk)
    Base.metadata.create_all(sqlite_engine)

    from src.database import connection as conn_mod
    test_factory = scoped_session(
        sessionmaker(
            bind=sqlite_engine, autoflush=False, expire_on_commit=False, future=True
        )
    )
    conn_mod.engine = sqlite_engine
    conn_mod.SessionLocal = test_factory

    yield sqlite_engine
    sqlite_engine.dispose()

@pytest.fixture(autouse=True)
def _clean_tables(engine):
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())

@pytest.fixture
def db_session(engine):
    factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    db = factory()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture
def role_repo(db_session):
    from src.repositories.user_repository import RoleRepository
    repo = RoleRepository(db_session)
    repo.ensure_default()
    db_session.commit()
    return repo

@pytest.fixture
def user_repo(db_session):
    from src.repositories.user_repository import UserRepository
    return UserRepository(db_session)

@pytest.fixture
def test_repo(db_session):
    from src.repositories.test_repository import TestRepository
    return TestRepository(db_session)

@pytest.fixture
def question_repo(db_session):
    from src.repositories.test_repository import QuestionRepository
    return QuestionRepository(db_session)

@pytest.fixture
def attempt_repo(db_session):
    from src.repositories.result_repository import TestAttemptRepository
    return TestAttemptRepository(db_session)

@pytest.fixture
def answer_repo(db_session):
    from src.repositories.result_repository import AttemptAnswerRepository
    return AttemptAnswerRepository(db_session)

@pytest.fixture
def answer_opt_repo(db_session):
    from src.repositories.result_repository import AttemptAnswerOptionRepository
    return AttemptAnswerOptionRepository(db_session)

@pytest.fixture
def auth_service(user_repo, role_repo):
    from src.services.auth_service import AuthService
    return AuthService(user_repo, role_repo)

@pytest.fixture
def quiz_service(test_repo, attempt_repo, answer_repo, answer_opt_repo):
    from src.services.quiz_service import QuizService
    return QuizService(test_repo, attempt_repo, answer_repo, answer_opt_repo)

@pytest.fixture
def test_service(test_repo, question_repo, attempt_repo):
    from src.services.test_service import TestService
    return TestService(test_repo, question_repo, attempt_repo)

@pytest.fixture
def teacher(auth_service, db_session):
    user = auth_service.register(
        email="teacher@example.com",
        password="password123",
        full_name="Teacher One",
        role="teacher",
    )
    db_session.commit()
    return user

@pytest.fixture
def student(auth_service, db_session):
    user = auth_service.register(
        email="student@example.com",
        password="password123",
        full_name="Student One",
        role="student",
    )
    db_session.commit()
    return user

@pytest.fixture
def sample_test(test_service, teacher, db_session):
    test_obj = test_service.create(
        owner_id=teacher.id,
        title="Mathematics",
        time_limit_minutes=30,
        description="Basic test",
        randomize=False,
    )
    test_service.add_question(
        test_obj, qtype="single",
        text="2 + 2 = ?",
        options=["3", "4", "5"],
        correct_indexes=[1],
    )
    test_service.add_question(
        test_obj, qtype="multiple",
        text="Even numbers",
        options=["1", "2", "3", "4"],
        correct_indexes=[1, 3],
    )
    test_service.publish(test_obj)
    db_session.commit()
    return test_obj

@pytest.fixture
def app(engine):
    from src.main import create_app
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()
