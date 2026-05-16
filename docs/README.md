# Quiz System Documentation

A Flask web application for creating and taking tests
with automatic result checking.

## Structure

```
docs/
├── README.md                ← you are here (index)
├── overview/                ← where to start and how it works
│   ├── getting-started.md
│   └── architecture.md
├── backend/                 ← DB, migrations, authorization, HTTP API
│   ├── database.md
│   ├── migrations.md
│   ├── auth.md
│   └── api-routes.md
├── frontend/                ← Jinja2 templates, CSS, JS
│   ├── frontend.md
│   └── error-pages.md
├── flows/                   ← user scenarios
│   ├── student-flow.md
│   └── teacher-flow.md
├── development/             ← how to develop and test
│   ├── testing.md
│   └── linting.md
└── operations/              ← running and deployment
    └── deployment.md
```

## Contents

### Overview - overview and installation

| Section | Description                                 |
|---------|---------------------------------------------|
| [Getting Started](overview/getting-started.md) | Installing PostgreSQL, config, first run    |
| [Architecture](overview/architecture.md) | Layered architecture, directories, data flow |

### Backend - server side

| Section | Description                                |
|---------|--------------------------------------------|
| [Database](backend/database.md) | Schema, tables, FKs, indexes               |
| [Migrations (Alembic)](backend/migrations.md) | Migration chain, commands                  |
| [Authorization and roles](backend/auth.md) | bcrypt, registration, login, guards        |
| [HTTP routes](backend/api-routes.md) | All endpoints with parameters and responses |

### Frontend - UI and templates

| Section | Description                        |
|---------|------------------------------------|
| [Templates and styles](frontend/frontend.md) | Jinja2, CSS, JS, smooth transitions |
| [Error pages](frontend/error-pages.md) | 4xx and 5xx handlers               |

### Flows - user scenarios

| Section | Description                          |
|---------|--------------------------------------|
| [Student flow](flows/student-flow.md) | Taking a test, history, result       |
| [Teacher flow](flows/teacher-flow.md) | Creating tests, questions, statistics |

### Development

| Section | Description               |
|---------|---------------------------|
| [Testing](development/testing.md) | pytest, fixtures, coverage |
| [Linters and code style](development/linting.md) | ruff, pylint, mypy        |

### Operations - running

| Section | Description                                    |
|---------|------------------------------------------------|
| [Deployment](operations/deployment.md) | Production setup, Docker, environment variables |

## Quick links

- Main project README: [`../README.md`](../README.md)
- Application entry point: [`../src/main.py`](../src/main.py)
- HTTP routes: [`../src/blueprints/`](../src/blueprints/)
- Migrations (the single source of the schema): [`../alembic/versions/`](../alembic/versions/)
