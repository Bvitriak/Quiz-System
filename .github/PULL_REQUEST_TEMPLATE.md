## Summary of changes

<!-- Briefly describe what was changed and why. -->

## Type of changes

- [ ] Bug fix
- [ ] New feature
- [ ] Refactoring (no behavior change)
- [ ] DB migration (Alembic)
- [ ] UI / templates / styles
- [ ] Tests
- [ ] Documentation (README, docs/)
- [ ] Configuration / CI / dependencies

## Related issues

Closes #

## Checklist

- [ ] `ruff check .` - no warnings
- [ ] `pylint src` - `10.00/10`
- [ ] `mypy .` - `Success`
- [ ] `pytest --cov=src --cov-fail-under=80` - all tests pass, coverage >= 80 %
- [ ] If a migration was added - verified `alembic upgrade head` and `alembic downgrade -1`
- [ ] If routes or models were touched - relevant `docs/*.md` updated
- [ ] If the environment changed - `.env.example` updated

## Screenshots (for UI changes)

<!-- Before / after, if templates or CSS were changed. -->

## Notes for the reviewer

<!-- Anything especially important to look at, any pitfalls. -->
