# Contributing

Thanks for your interest in Quiz System!

## Getting started

1. Read [`docs/getting-started.md`](../docs/getting-started.md) - installation,
   PostgreSQL, migrations, first run.
2. Bring up the environment and make sure `ruff`, `pylint`,
   `mypy`, and `pytest` are all green.

## Workflow

```bash
# 1. Create a branch from main
git checkout -b feat/short-description

# 2. Make changes, run linters and tests
ruff check .
pylint src
mypy .
pytest --cov=src --cov-fail-under=80

# 3. If you changed models - create a migration
alembic revision --autogenerate -m "description"
alembic upgrade head && alembic downgrade -1 && alembic upgrade head

# 4. Commit
git commit -m "feat: short description"

# 5. Push and open a PR
git push origin HEAD
```

## Commit style

We use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When                       |
|---------|----------------------------|
| `feat:` | new feature                |
| `fix:` | bug fix                    |
| `refactor:` | no behavior change         |
| `docs:` | docs only                  |
| `test:` | tests only                 |
| `ci:` | GitHub Actions             |
| `deps:` | dependency updates         |
| `chore:` | other (formatting, configs) |

## Pull request

- Fill out the checklist in the PR template.
- One PR = one logical change. Split large tasks up.
- Attach screenshots for UI changes.
- Test coverage must stay **>= 80 %** - CI enforces this.

## Code style

See [`docs/linting.md`](../docs/linting.md).

- Line length - **100 characters**.
- Imports: standard library -> third-party -> `src.*`.
- Service public APIs are covered by type hints; mypy must stay clean.

## Architecture

Before making large changes, read
[`docs/architecture.md`](../docs/architecture.md) - the layered structure;
layers must not be mixed (HTTP must not reach into SQLAlchemy directly,
bypassing services).

## Tests

See [`docs/testing.md`](../docs/testing.md). New features require:

- **Unit tests** for services (with mocks).
- **Integration tests** for repositories and services (with a temporary DB).
- **GUI tests** for new HTTP routes.

## Issues

Before opening an issue, check that:

- one isn't already open;
- the answer isn't already in [`docs/`](../docs/);
- you filled out the template (bug or feature request).

## Security

If you find a vulnerability - **do not open a public issue**.
See [`SECURITY.md`](SECURITY.md).
