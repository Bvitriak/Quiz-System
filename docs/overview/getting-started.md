# Getting Started

Running the project locally from scratch.

## Requirements

- **Python 3.10+**
- **PostgreSQL 14+** (16 works well)
- **pip** to install dependencies
- macOS / Linux / Windows (on Windows activate the venv with `.venv\Scripts\activate`)

## Steps

### 1. Clone the repository

```bash
git clone https://github.com/Bvitriak/quiz-system.git
cd quiz-system
```

### 2. Virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

This installs `flask`, `sqlalchemy`, `alembic`, `psycopg2-binary`, `bcrypt`,
`python-dotenv` + dev tools (`pytest`, `pytest-cov`, `pylint`, `mypy`).

### 4. Start PostgreSQL

```bash
brew install postgresql@16          # one time
brew services start postgresql@16
```

Check:
```bash
pg_isready -h localhost -p 5432
```

### 5. Create the user and the database

```bash
psql -d postgres <<'SQL'
CREATE USER quiz_user WITH PASSWORD 'quiz_pass_123';
CREATE DATABASE quiz_db OWNER quiz_user;
GRANT ALL PRIVILEGES ON DATABASE quiz_db TO quiz_user;
SQL
```

> Alternative: use your system login and skip `CREATE USER`.

### 6. Create `.env`

```bash
cp .env.example .env
```

Open `.env` and set your own `DB_PASSWORD` and `APP_SECRET_KEY`.
A full list of variables is in [deployment.md](deployment.md).

### 7. Apply migrations

```bash
alembic upgrade head
```

This creates all tables and seeds the `student` / `teacher` roles.
More in [migrations.md](migrations.md).

### 8. Run the application

```bash
python3 -m src.main
```

Open **http://127.0.0.1:8000** in the browser.

## Cheat sheet

```bash
# Run
python3 -m src.main

# Tests + coverage
pytest --cov=src --cov-report=term-missing

# Linters
ruff check . && pylint src && mypy .

# Migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic history
```

## Possible issues

| Error | Solution                                                  |
|-------|-----------------------------------------------------------|
| `role "quiz_user" does not exist` | Step 5 - create the user                                  |
| `database "quiz_db" does not exist` | Step 5 - `CREATE DATABASE`                                |
| `relation "roles" does not exist` | Step 7 - `alembic upgrade head`                           |
| `could not connect to server` | PostgreSQL is not running: `brew services start postgresql@16` |
| `column tests.max_attempts does not exist` | Latest migrations not applied - `alembic upgrade head`    |
