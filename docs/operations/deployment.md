# Deployment

## Environment variables

Full template - [`.env.example`](../.env.example).

| Variable | Purpose | Default                |
|----------|---------|------------------------|
| `DB_HOST` | PostgreSQL host | `localhost`            |
| `DB_PORT` | port | `5432`                 |
| `DB_NAME` | DB name | `quiz_db`              |
| `DB_USER` | user | `quiz_user`            |
| `DB_PASSWORD` | password | (empty)                |
| `DATABASE_URL` | full URL, takes priority | -                      |
| `APP_SECRET_KEY` | Flask cookie signing key | `dev-secret-change-me` |
| `DEBUG` | `true` → Flask debug + echo SQL | `false`                |
| `PASS_THRESHOLD` | % correct for "passed" | `60`                   |

`DATABASE_URL` always wins over `DB_*`. The `postgresql://` prefix is
automatically expanded to `postgresql+psycopg2://` in
[`src/config.py`](../src/config.py).

## Local run

See [getting-started.md](getting-started.md).

```bash
python3 -m src.main
```

This starts the **Flask dev server** on `127.0.0.1:8000`. **Do not use
for production** - it is single-threaded, cannot handle concurrent
requests properly, and warns about it itself.

## Production: WSGI

In production run via a WSGI server. Example with gunicorn:

```bash
pip install gunicorn

gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 60 \
  "src.main:create_app()"
```

Alternatively uwsgi/waitress - your choice.

## Production: PostgreSQL

1. Do not use `psycopg2-binary` in production - install **`psycopg2`**
   (compiled version):
   ```bash
   pip install -e ".[prod]"
   ```
   In `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   prod = ["psycopg2>=2.9"]
   ```

2. Create a **dedicated DB user** with minimal privileges on its own
   database. Do not use the `postgres` superuser for the application.

3. **Backups** via `pg_dump` on cron.

4. Enable **SSL** if the DB is on a separate server.

## Docker

The repository already contains `Dockerfile` and `compose.yaml`.

```bash
docker compose up -d db        # PostgreSQL only
docker compose run --rm migrate   # apply migrations
docker compose up app          # run the application
```

> Note: these files are leftovers from the previous Tkinter version and may
> require adaptation for Flask. Check `Dockerfile.CMD` - in production it
> should be `gunicorn`, not `python -m src.main`.

## Pre-production release checklist

- [ ] A strong `APP_SECRET_KEY` is generated (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] `DEBUG=false`
- [ ] `DATABASE_URL` points to the prod DB with a strong password
- [ ] Started via a WSGI server (gunicorn / uwsgi)
- [ ] Reverse proxy (nginx) for HTTPS and static files
- [ ] Cookies marked `Secure` + `HttpOnly` (in Flask
      `SESSION_COOKIE_HTTPONLY=True` by default; set `SESSION_COOKIE_SECURE=True` manually)
- [ ] The server is monitored (uptime, errors, DB metrics)
- [ ] DB backup script works and is verified (restore test)
- [ ] CI runs `pytest`, `ruff`, `pylint`, `mypy` before deployment
- [ ] All migrations are applied: `alembic current` == latest revision

## Security notes

- Passwords are hashed with bcrypt (see [auth.md](auth.md)).
- The Flask session is a signed cookie. It cannot be forged without
  `APP_SECRET_KEY`, but its **contents are readable** (it is base64).
  Do not put secrets in it.
- There is no out-of-the-box CSRF protection. For production it is
  recommended to add `flask-wtf` or to verify the token manually on
  POST routes.
- SQL injection is excluded - parameterized queries via SQLAlchemy ORM
  are used everywhere.
- XSS - Jinja2 escapes by default. Do not use `|safe` unnecessarily.

## CI/CD

`.github/workflows/` contains:
- `ci.yml` - tests and linters
- `docker.yml` - Docker image build

Before merging, a PR must:
1. Pass all tests (`pytest`)
2. Have no ruff/pylint/mypy warnings
3. Maintain coverage ≥ 80%
