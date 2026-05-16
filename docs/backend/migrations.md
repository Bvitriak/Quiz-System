# Migrations (Alembic)

All DB schema changes are managed by Alembic.
The connection URL is injected in [`alembic/env.py`](../alembic/env.py) from
`src.config.settings`, which reads `.env`.

## Migration chain

| Revision | File | Contents                                                    |
|----------|------|-------------------------------------------------------------|
| 0001 | `…_create_roles.py` | `roles`                                                     |
| 0002 | `…_create_users.py` | `users` + `idx_users_email`                                 |
| 0003 | `…_create_sessions.py` | `sessions` + indexes                                        |
| 0004 | `…_create_tests.py` | `tests` + indexes                                           |
| 0005 | `…_create_questions.py` | `questions`, `question_options`, `question_text_answers`    |
| 0006 | `…_create_test_attempts.py` | `test_attempts`, `attempt_answers`, `attempt_answer_options` |
| 0007 | `…_create_test_status_history.py` | `test_status_history`                                       |
| 0008 | `…_seed_default_roles.py` | INSERT `student` / `teacher`                                |
| 0009 | `…_add_max_attempts.py` | `tests.max_attempts` column                                 |

The files live in [`alembic/versions/`](../alembic/versions/).

## Commands

```bash
# Apply all
alembic upgrade head

# Roll back one
alembic downgrade -1

# Roll back to a specific revision
alembic downgrade a1b2c3d4e5f6

# Current revision in the DB
alembic current

# History
alembic history

# Create an empty migration
alembic revision -m "description"

# Generate a migration from ORM changes
alembic revision --autogenerate -m "description"

# Mark the DB as being at head without running SQL
# (used when the schema has already been synchronized manually)
alembic stamp head
```

## Alembic config files

- [`alembic.ini`](../alembic.ini) - shared settings, `script_location = alembic`,
  `file_template = %(year)d%(month).2d%(day).2d_%(hour).2d%(minute).2d_%(rev)s_%(slug)s`.
  The `sqlalchemy.url` field is a placeholder, the real value comes from `env.py`.
- [`alembic/env.py`](../alembic/env.py) - imports all models so they end up
  in `Base.metadata`, and overrides the URL from `src.config.settings`.
- [`alembic/script.py.mako`](../alembic/script.py.mako) - Jinja template for new
  migration files.

## Rules

1. **Never edit an applied migration** - create a new one.
2. **Reversibility** - every migration must have a working `downgrade()`.
3. **Revision name** - short hex (12 characters). The chain is set via
   `down_revision`.
4. **Seeds and DDL in separate migrations** (DDL is easy to roll back, seeds separately).
5. **autogenerate** is convenient, but always **review the generated SQL manually**.
