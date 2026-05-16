# Architecture

Layered architecture with explicit separation of responsibilities.
Dependencies point top-down - upper layers know about lower ones, but not vice versa.

## Layer diagram

```
┌───────────────────────────────────────────────────┐
│  Templates (Jinja2) + Static (CSS / JS)           │  Presentation
├───────────────────────────────────────────────────┤
│  Flask routes  (src/main.py)                      │  HTTP layer
├───────────────────────────────────────────────────┤
│  Controllers   (src/controllers/*)                │  Orchestration
├───────────────────────────────────────────────────┤
│  Services      (src/services/*)                   │  Business logic
├───────────────────────────────────────────────────┤
│  Repositories  (src/repositories/*)               │  Data access
├───────────────────────────────────────────────────┤
│  SQLAlchemy Models (src/models/*)                 │  ORM
├───────────────────────────────────────────────────┤
│  PostgreSQL                                       │  Storage
└───────────────────────────────────────────────────┘
```

## Layer responsibilities

### Templates / Static - `src/templates/`, `src/static/`
- Jinja2 templates and CSS/JS. No logic beyond formatting and small
  frontend features (timer, question type switcher, dropdown menu in the topbar).

### Flask routes - `src/main.py`
- HTTP routing, parsing of `request.form`, template rendering.
- `login_required(role=…)` decorator - authentication guard.
- Per-request `SessionLocal()` via `g.db` (`before_request` / `teardown_request`).
- DI factories `_auth() / _quiz() / _tests()` build controllers bound to the current DB session.
- Error handlers for 400/401/403/404/405/500/502/503/504/507.

### Controllers - `src/controllers/`
- Thin wrappers around services. Validate primitive parameters (via
  `utils.validators`) and delegate the logic.
- Do not call `commit()` - that is the route handler's job via `g.db`.

### Services - `src/services/`
- Business logic, independent of Flask and requests.
- `AuthService` - bcrypt password hashing, registration, login.
- `TestService` - CRUD of tests and questions, publish/draft, statistics.
- `QuizService` - start an attempt, save answers, scoring, attempt limit.

### Repositories - `src/repositories/`
- DB-access layer, hides SQLAlchemy from services.
- `BaseRepository[T]` - generic CRUD methods.
- Concrete repositories: `UserRepository`, `RoleRepository`,
  `TestRepository`, `QuestionRepository`, `TestAttemptRepository`,
  `AttemptAnswerRepository`, `AttemptAnswerOptionRepository`.

### Models - `src/models/`
- SQLAlchemy declarative models with `Mapped[...]`/`mapped_column`.
- UI properties: `is_teacher`, `status_label`, `correct_indexes`,
  `success_percent`, etc.
- `TYPE_CHECKING` imports for forward-refs (mypy-friendly).

## Dependency injection

In `main.py` dependencies are assembled dynamically on every request so that
each controller receives a fresh DB session:

```python
def _quiz() -> QuizController:
    return QuizController(QuizService(
        TestRepository(g.db),
        TestAttemptRepository(g.db),
        AttemptAnswerRepository(g.db),
        AttemptAnswerOptionRepository(g.db),
    ))
```

Advantages:
- All `commit()` calls are managed in one place - `teardown_request`.
- In tests it is easy to swap `g.db` for the test engine's session.

## Configuration - `src/config.py`

The `Settings` dataclass reads `.env` via `python-dotenv` or the system
environment variables. Fields:

| Field | Source | Default |
|-------|--------|---------|
| `database_url` | `DATABASE_URL` or `DB_*` | `postgresql+psycopg2://quiz_user:@localhost:5432/quiz_db` |
| `secret_key` | `APP_SECRET_KEY` | `"dev-secret-change-me"` |
| `debug` | `DEBUG` | `false` |
| `pass_threshold` | `PASS_THRESHOLD` | `60` |

## DB sessions

`src/database/connection.py` creates:
- `engine` - one per process, `pool_pre_ping=True`
- `SessionLocal` - `scoped_session`, bound to thread/greenlet

In Flask, `g.db = SessionLocal()` is opened in `before_request`, committed in
`teardown_request` (or rolled back on exception), then `SessionLocal.remove()`.
