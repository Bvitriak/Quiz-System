# Testing

Uses **pytest**. Coverage target: **≥ 80%**.

## Structure

```
tests/
├── conftest.py            - shared fixtures
├── unit/                  - pure unit tests with MagicMock
│   ├── test_validators.py
│   ├── test_auth_service.py
│   └── test_controllers.py
├── integration/           - services + real repositories + temporary DB
│   ├── test_repositories.py
│   ├── test_quiz_service.py
│   └── test_test_service.py
└── gui/                   - Flask test client
    ├── test_auth_routes.py
    ├── test_student_routes.py
    ├── test_teacher_routes.py
    └── test_error_pages.py
```

## Running

```bash
pytest                                      # all tests
pytest --cov=src --cov-report=term-missing  # with detailed coverage
pytest --cov=src --cov-report=html          # html report

pytest tests/unit/                          # only unit tests
pytest tests/integration/
pytest tests/gui/

pytest -k "auth"                            # by name substring
pytest -k "test_login_then_logout"          # one specific test
pytest -x                                   # stop on first failure
pytest -v                                   # verbose output
```

## Fixtures (`conftest.py`)

### Temporary DB

```python
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
```

This must happen BEFORE the first import of `src.*`, so that
`src.config.settings` reads the test URL.

**SQLite caveats:**

1. `BigInteger PRIMARY KEY` does not auto-increment in SQLite.
   Via `@compiles(BigInteger, "sqlite")` we rewrite the type to
   `INTEGER` - then SQLite uses ROWID auto-increment.

2. `PRAGMA foreign_keys=ON` is enabled via `event.listen(..., "connect", ...)` -
   otherwise SQLite silently ignores `ON DELETE CASCADE`.

### Main engine

`engine` is session-scoped. It is created once and immediately patches
`src.database.connection.engine` and `SessionLocal` to the test objects.
This is critical: `src.main` imports `SessionLocal` by name, and the swap
**must happen before the first import of `main`**.

### Table cleanup

`_clean_tables` is autouse - it deletes all rows after each test
(the DB structure stays). This gives isolation without re-creating tables.

### `db_session`

A fresh `Session` for each test. Used directly in integration tests.

### Domain fixtures

- `role_repo`, `user_repo`, `test_repo`, `question_repo`, `attempt_repo`,
  `answer_repo`, `answer_opt_repo` - wrap `db_session`.
- `auth_service`, `quiz_service`, `test_service` - assemble services from repos.
- `teacher`, `student` - pre-registered users.
- `sample_test` - a published test with two questions (single + multiple).

### Flask test client

- `app` - calls `create_app()` after the `engine` fixture has already
  patched the `connection` module.
- `client` - `app.test_client()`.

## Test style

### Unit tests - mocks

```python
def _make_service(role_lookup=None, by_email=None):
    users = MagicMock()
    users.by_email.return_value = by_email
    roles = MagicMock()
    roles.by_code.return_value = role_lookup
    return AuthService(users, roles), users, roles


def test_register_creates_user_with_hashed_password():
    role = MagicMock(id=1)
    svc, users, _ = _make_service(role_lookup=role)
    user = svc.register("a@b.io", "secret123", "Anna", "student")
    users.add.assert_called_once()
    assert bcrypt.checkpw(b"secret123", user.password_hash.encode())
```

### Integration - real DB

```python
def test_full_pass(self, quiz_service, sample_test, student, db_session):
    attempt = quiz_service.start_attempt(student.id, sample_test.id)
    quiz_service.save_answer(attempt, sample_test.questions[0], 1)
    db_session.commit()
    quiz_service.finish_attempt(attempt)
    assert attempt.correct_count == 1
```

### GUI - Flask test client

```python
def test_register_student_redirects_to_student_area(client):
    r = client.post("/register", data={
        "email": "newstud@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "full_name": "New Student",
        "role": "student",
    }, follow_redirects=False)
    assert r.status_code == 302
    assert "/student" in r.headers["Location"]
```

## Coverage

- Registration / login / validators (including strong password)
- Start/finish of an attempt, scoring single/multiple (partial)/text
- Test availability window, delayed result display
- Attempt limit with a clear message
- CRUD of tests and questions, publish/draft + record into `TestStatusHistory`
- Student statistics
- Route protection: `@login_required`, `@require_test_owner`
- Full student flow (register → start → answer → finish → result)
- Error pages (404, 405)
- Security: CSRF, rate limit, `/healthz` when the DB is down, security headers

## CSRF and Limiter in tests

The global `app` fixture in `tests/conftest.py` sets
`WTF_CSRF_ENABLED=False` - convenient for most scenarios. If you need
to test CSRF protection specifically, use the local `csrf_app` fixture
(see `tests/gui/test_security.py`):

```python
@pytest.fixture
def csrf_app(engine):
    from src.main import create_app
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = True
    yield flask_app
```

Flask-Limiter uses in-memory storage. Limits are reset between tests:

```python
from src.utils.rate_limit import limiter
limiter.reset()
```

## Simulating a DB failure

`/healthz` is mocked by replacing `src.main.SessionLocal` with a class whose
`execute()` raises `SQLAlchemyError`:

```python
with patch.object(main_mod, "SessionLocal", broken_factory):
    r = client.get("/healthz")
assert r.status_code == 503
```
