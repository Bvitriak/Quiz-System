# Linters and code style

## Tools

| Tool | What it checks | Config                              |
|------|----------------|-------------------------------------|
| **ruff** | style (PEP 8), import order, unused names, basic analysis | `pyproject.toml` (`[tool.ruff*]`)   |
| **pylint** | deep analysis, design, unused arguments | `pyproject.toml` (`[tool.pylint.*]`) |
| **mypy** | static typing | `pyproject.toml` (`[tool.mypy]`)    |

All three tools are configured in `pyproject.toml` - there are no
separate dotfiles in the project root.

## Running

```bash
ruff check . # style + imports + basic analysis
pylint src   # deep analysis
mypy .       # types

# all together
ruff check . && pylint src && mypy .
```

Auto-fix simple issues (import order, removal of unused names,
small style fixes):

```bash
ruff check --fix .
```

## Expected output

- **ruff**: `All checks passed!`
- **pylint**: `Your code has been rated at 10.00/10`
- **mypy**: `Success: no issues found in 22 source files`

## Settings

### Ruff

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
extend-exclude = [
    "alembic",
    "tests",
    "build",
    "dist",
    ".venv",
    "venv",
    "__pycache__",
]

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
ignore = [
    "E203",
    "E501",
]
```

Active rule groups:
- **E/W** - pycodestyle (PEP 8 errors and warnings)
- **F** - pyflakes (unused imports/variables, typos)
- **I** - isort (import order)

You may additionally enable:
- `"B"` - flake8-bugbear (anti-pattern detector)
- `"UP"` - pyupgrade (syntax modernization for Python 3.10+)
- `"SIM"` - flake8-simplify

### Pylint

```toml
[tool.pylint.main]
py-version = "3.10"
ignore-paths = ["alembic/.*", "tests/.*"]

[tool.pylint.messages_control]
disable = [
    "missing-module-docstring",
    "missing-class-docstring",
    "missing-function-docstring",
    "too-few-public-methods",
    "too-many-arguments",
    "too-many-locals",
    "too-many-positional-arguments",
    "too-many-instance-attributes",
    "import-outside-toplevel",
    "cyclic-import",
    "unused-argument",
    "too-many-statements",
    "too-many-branches",
    "too-many-return-statements",
    "unsubscriptable-object",
    "not-callable",
]

[tool.pylint.format]
max-line-length = 100
```

### Mypy

```toml
[tool.mypy]
python_version = "3.10"
strict = false
ignore_missing_imports = true
explicit_package_bases = true
namespace_packages = true
mypy_path = "."
exclude = "(alembic/|tests/)"
```

## Line length - 100

The PEP 8 default (79) is excessively narrow for modern monitors.
Aligned everywhere: `ruff.line-length = 100`,
`pylint.format.max-line-length = 100`.

## SQLAlchemy 2.0 and pylint

`Mapped[list["Question"]]` annotations cause pylint to raise
`unsubscriptable-object` - a known false positive,
disabled in `disable`.

## Forward references

The models use `if TYPE_CHECKING:` to import classes that are needed
only in annotations. This breaks cyclic imports and gives mypy
full types.

## What is NOT linted

Intentionally excluded from all tools:
- `alembic/` - auto-generated code
- `tests/` - lenient rules (line length, imports inside functions)

## Pre-commit (optional)

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks: [{id: mypy}]
```

Install: `pre-commit install`.
