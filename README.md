# Quiz System - Knowledge Testing System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Flask web application for creating and taking tests with automatic
result checking and data storage in PostgreSQL.
Developed as part of the "Information Systems Tools" course.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running](#running)
- [Database Migrations](#database-migrations)
- [Linters and Code Checks](#linters-and-code-checks)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [License](#license)

## Features

### For Teachers
- Create and edit tests
- Manage questions of three types: single choice, multiple choice, text answer
- Editable scores for each question
- Configure time limit and availability window (UTC)
- "Show result immediately" / delayed result option
- Publish a test / return to draft (change history in `test_status_history`)
- View student statistics

### For Students
- List of available (published) tests with description and passing score
- Take a test with a countdown timer and question navigation
- Automatic checking with partial scoring for multiple choice
- Text answers are compared to the reference value case- and whitespace-insensitively
- History of attempts with all tries
- Password recovery page (`/forgot-password`) with administrator contact

### Security
- CSRF tokens in all forms (Flask-WTF)
- Rate limiting: `/login` — 5 attempts / 15 minutes, `/register` — 10 / hour, `/forgot-password` — 20 / hour
- Security HTTP headers: CSP, X-Frame-Options, Strict-Transport-Security (prod)
- Secure cookies in prod, HttpOnly + SameSite=Lax always
- Fail-fast on default `APP_SECRET_KEY` outside `DEBUG` mode
- `/healthz` — JSON endpoint with DB status (for k8s/Docker healthcheck)

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.10+ |
| **Web** | Flask 3 (Jinja2, Werkzeug) |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **DB** | PostgreSQL 14+ |
| **Password hashing** | bcrypt |
| **CSRF** | Flask-WTF |
| **Rate limiting** | Flask-Limiter |
| **Linters** | ruff, pylint, mypy |
| **Testing** | pytest |

## Architecture

Layered architecture (presentation → controllers → services → repositories → ORM → DB).

```
┌──────────────────────────────────────────────┐
│  Templates + Static (Jinja2 / CSS / JS)      │  ← UI
├──────────────────────────────────────────────┤
│  Flask routes (src/main.py)                  │  ← HTTP
├──────────────────────────────────────────────┤
│  Controllers                                 │  ← orchestration
├──────────────────────────────────────────────┤
│  Services (AuthService, QuizService, …)      │  ← business logic
├──────────────────────────────────────────────┤
│  Repositories (BaseRepository[T] + subclasses)│ ← data access
├──────────────────────────────────────────────┤
│  SQLAlchemy Models (Base.metadata)           │  ← ORM
├──────────────────────────────────────────────┤
│  PostgreSQL                                  │  ← storage
└──────────────────────────────────────────────┘
```

## Quick Start

```bash
git clone https://github.com/Bvitriak/quiz-system.git
cd quiz-system

cp .env.example .env # edit DB_PASSWORD and APP_SECRET_KEY

pip install -e ".[dev]"

psql -d postgres -c "CREATE USER quiz_user WITH PASSWORD 'quiz_pass_123';"
psql -d postgres -c "CREATE DATABASE quiz_db OWNER quiz_user;"

alembic upgrade head

python3 -m src.main
```

Open in browser: **http://127.0.0.1:8000**

## Installation

### Requirements
- Python 3.10+
- PostgreSQL 14+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Bvitriak/quiz-system.git
cd quiz-system

# 2. Virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate # Linux/macOS
.venv\Scripts\activate # Windows

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Create .env
cp .env.example .env

# 5. Prepare PostgreSQL
psql -d postgres <<'SQL'
CREATE USER quiz_user WITH PASSWORD 'quiz_pass_123';
CREATE DATABASE quiz_db OWNER quiz_user;
GRANT ALL PRIVILEGES ON DATABASE quiz_db TO quiz_user;
SQL

# 6. Apply migrations
alembic upgrade head
```

If you work under your own system PostgreSQL login you can skip
`CREATE USER` and set in `.env`
`DATABASE_URL=postgresql+psycopg2://$(whoami)@localhost:5432/quiz_db`.

## Running

```bash
python3 -m src.main
```

You should see:

```
 * Running on http://127.0.0.1:8000
 * Debug mode: on / off  (depends on DEBUG in .env)
```

To stop: `Ctrl+C`.

### Environment variables (`.env`)

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=quiz_db
DB_USER=quiz_user
DB_PASSWORD=quiz_pass_123

APP_SECRET_KEY=any-long-random-string # MUST be overridden in prod
DEBUG=false # true - auto-reload + echo of SQL queries
PASS_THRESHOLD=60 # % of correct answers for "passed" status
EXCELLENT_THRESHOLD=80 # % for "Excellent result" feedback
LOG_FILE= # optional: path to log file (RotatingFileHandler, 10 MB × 5)
ADMIN_CONTACT=admin@example.com # shown on "Forgot password" page
```

## Database Migrations

The URL is taken from `src.config.settings` (which reads `.env`).

```bash
alembic upgrade head # apply all migrations
alembic downgrade -1 # roll back the last one
alembic current # current revision
alembic history # history
alembic revision --autogenerate -m "msg" # generate a migration from ORM
alembic stamp head # mark as head (if the schema was applied manually)
```

Migration chain:

| # | Description |
|---|-------------|
| 0001 | `roles` |
| 0002 | `users` (+ `idx_users_email`) |
| 0003 | `sessions` |
| 0004 | `tests` |
| 0005 | `questions` + `question_options` + `question_text_answers` |
| 0006 | `test_attempts` + `attempt_answers` + `attempt_answer_options` |
| 0007 | `test_status_history` |
| 0008 | seed roles `student` / `teacher` |
| 0009 | `tests.max_attempts` |
| 0010 | `tests.availability_start/end`, `show_result_immediately`, `description` → Text |

## Linters and Code Checks

```bash
ruff check .
pylint src
mypy .
```

Auto-fix simple issues (import order, unused imports):
```bash
ruff check --fix .
```

All configuration lives in [pyproject.toml](pyproject.toml) - sections
`[tool.ruff*]`, `[tool.pylint.*]`, `[tool.mypy]`. Maximum line length is 100.
The `alembic/` and `tests/` directories are excluded from linter checks.

## Project Structure

```
quiz-system/
├── src/
│   ├── main.py                     # Flask app factory + blueprint registration
│   ├── config.py                   # Settings (reads .env)
│   ├── blueprints/                 # HTTP routes, split by role
│   │   ├── auth.py                 # /, /register, /login, /logout, /dashboard
│   │   ├── student.py              # /student/* — test list, attempts, history
│   │   ├── teacher.py              # /teacher/* — test CRUD, scheduling
│   │   └── _helpers.py             # controller factories, formatters
│   ├── database/
│   │   └── connection.py           # engine + SessionLocal (scoped)
│   ├── models/                     # SQLAlchemy models
│   │   ├── base.py                 # DeclarativeBase
│   │   ├── user.py                 # Role, User, SessionToken
│   │   ├── test.py                 # Test, TestStatusHistory
│   │   ├── question.py             # Question, QuestionOption, QuestionTextAnswer
│   │   ├── answer.py               # re-export for compatibility
│   │   └── result.py               # TestAttempt, AttemptAnswer, AttemptAnswerOption
│   ├── repositories/               # CRUD layer
│   │   ├── base_repository.py      # BaseRepository[T]
│   │   ├── user_repository.py      # UserRepository, RoleRepository
│   │   ├── test_repository.py      # TestRepository, QuestionRepository, …
│   │   └── result_repository.py    # TestAttemptRepository, AttemptAnswer*Repository
│   ├── services/                   # Business logic
│   │   ├── auth_service.py         # registration/login (bcrypt)
│   │   ├── test_service.py         # CRUD of tests and questions, publishing, statistics
│   │   ├── quiz_service.py         # attempts, answers, scoring
│   │   └── stats_service.py        # compatibility alias
│   ├── controllers/                # Thin wrappers over services
│   │   ├── auth_controller.py
│   │   ├── test_controller.py
│   │   └── quiz_controller.py
│   ├── utils/
│   │   ├── validators.py           # validate_email / password / role
│   │   ├── timer.py                # remaining attempt time calculation
│   │   ├── text_match.py           # normalization and comparison of text answers
│   │   ├── decorators.py           # @login_required, @require_test_owner
│   │   └── logging_config.py       # logging setup
│   ├── templates/                  # Jinja2 templates
│   │   ├── auth/                   # index, login, register
│   │   ├── student/                # tests, test_take, result, history
│   │   ├── teacher/                # tests, create, edit, question_new, availability, students
│   │   └── errors/                 # 400, 401, 403, 404, 405, 500, 502, 503, 504, 507
│   └── static/                     # CSS / JS
│       ├── css/                    # auth.css, student.css, teacher.css, errors.css
│       └── js/                     # auth.js, student.js, teacher.js, topbar.js, errors.js
│
├── alembic/                        # Migrations
│   ├── env.py
│   ├── script.py.mako
│   ├── README
│   └── versions/                   # 0001…0010 — schema + role seed
│
├── tests/                          # pytest
│   ├── conftest.py
│   ├── unit/                       # validators, controllers, auth_service
│   ├── integration/                # quiz/test/scoring services
│   └── gui/                        # Flask routes (auth/student/teacher/owner)
│
├── docs/                           # documentation
├── alembic.ini
├── pyproject.toml                  # Dependencies + config
├── .env.example
├── .gitignore
├── .dockerignore
├── compose.yaml                    # Docker Compose
├── Dockerfile
├── LICENSE
└── README.md
```

## Documentation

Detailed documentation lives in the [`docs/`](docs/) directory:

| Category | Files |
|----------|-------|
| **Overview** | [getting-started](docs/overview/getting-started.md) · [architecture](docs/overview/architecture.md) |
| **Backend** | [database](docs/backend/database.md) · [migrations](docs/backend/migrations.md) · [auth](docs/backend/auth.md) · [api-routes](docs/backend/api-routes.md) |
| **Frontend** | [frontend](docs/frontend/frontend.md) · [error-pages](docs/frontend/error-pages.md) |
| **Flows** | [student-flow](docs/flows/student-flow.md) · [teacher-flow](docs/flows/teacher-flow.md) |
| **Development** | [testing](docs/development/testing.md) · [linting](docs/development/linting.md) |
| **Operations** | [deployment](docs/operations/deployment.md) |

Index with descriptions of all files: [`docs/README.md`](docs/README.md).

## Contributing

Before opening a PR, read [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md). At minimum:

```bash
ruff check .                 # must report "All checks passed!"
pytest tests -q              # 100% green
pytest tests --cov=src       # coverage ≥ 80%
```

## License

The project is distributed under the MIT license. Details are in the [LICENSE](LICENSE) file.

---

**Developed by MTI student Vitriak Bogdan Olegovich, group OKBI-204b**
*Course: Information Systems Tools 2026*
