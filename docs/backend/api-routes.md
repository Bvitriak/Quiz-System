# HTTP routes

Routes are split into blueprints in [`src/blueprints/`](../../src/blueprints/):
[`auth.py`](../../src/blueprints/auth.py), [`student.py`](../../src/blueprints/student.py),
[`teacher.py`](../../src/blueprints/teacher.py). Registration is in
[`src/main.py`](../../src/main.py).

For a role-based route, the `login_required(role=…)` decorator requires:
- a session cookie with `user_id`
- a user role matching the parameter (`student` or `teacher`)

On violation - redirect to `/login` or `/dashboard`.

## Public

| Method | Path | Description | Template               |
|--------|------|-------------|------------------------|
| GET | `/` | Landing page | `auth/index.html`      |
| GET, POST | `/register` | Registration (`role` ∈ student/teacher) | `auth/register.html`   |
| GET, POST | `/login` | Login | `auth/login.html`      |
| GET, POST | `/logout` | Logout (clears session) | redirect               |
| GET | `/dashboard` | Redirect to `/student` or `/teacher` by role | -                      |

### POST `/register`

| Field | Required | Description                  |
|-------|----------|------------------------------|
| `email` | yes | lowercased                   |
| `password` | yes | min 6 characters             |
| `password_confirm` | yes | must match `password`        |
| `full_name` | yes | non-empty string             |
| `role` | yes | `student` or `teacher`       |

Returns 302 - `/student` (or `/teacher`).

### POST `/login`

| Field | Required |
|-------|----------|
| `email` | yes     |
| `password` | yes     |

## Student (`role="student"`)

| Method | Path | Description | Template                  |
|--------|------|-------------|---------------------------|
| GET | `/student` | List of available tests | `student/tests.html`      |
| GET | `/student/history` | Attempt history | `student/history.html`    |
| POST | `/student/tests/<test_id>/start` | Create an attempt, redirect to question 1 | -                         |
| GET, POST | `/student/attempts/<aid>/question/<n>` | A single question. POST saves the answer | `student/test_take.html`  |
| POST | `/student/attempts/<aid>/finish` | Finish the attempt | -                         |
| GET | `/student/attempts/<aid>/result` | Result with answer breakdown | `student/result.html`     |

## Teacher (`role="teacher"`)

| Method | Path | Description | Template                      |
|--------|------|-------------|-------------------------------|
| GET | `/teacher` | My tests | `teacher/tests.html`          |
| GET | `/teacher/students` | Student statistics | `teacher/students.html`       |
| GET, POST | `/teacher/tests/new` | Create a test | `teacher/create.html`         |
| GET, POST | `/teacher/tests/<id>/edit` | Edit a test | `teacher/edit.html`           |
| GET, POST | `/teacher/tests/<id>/questions/new` | Add a question | `teacher/question_new.html`   |
| GET, POST | `/teacher/tests/<id>/questions/<qid>/edit` | Edit a question | `teacher/question_new.html`   |
| POST | `/teacher/tests/<id>/questions/<qid>/delete` | Delete a question | -                             |
| GET, POST | `/teacher/tests/<id>/availability` | Availability settings | `teacher/availability.html`   |

### Fields of `POST /teacher/tests/new` and `/edit`

| Field | Type | Description                                                     |
|-------|------|-----------------------------------------------------------------|
| `title` | string | name                                                            |
| `time_limit_minutes` | int > 0 | timer                                                           |
| `description` | string | optional                                                        |
| `randomize` | checkbox | `shuffle_questions`                                             |
| `action` | string | `draft` / `publish` / `add:single` / `add:multiple` / `add:text` |

### Fields when adding a question

| Field | Description                                                          |
|-------|----------------------------------------------------------------------|
| `type` | `single` / `multiple` / `text`                                       |
| `text` | question text                                                        |
| `option` | list of options (for single/multiple, via `request.form.getlist`)    |
| `correct` | indexes of the correct options                                       |
| `correct_text` | (ignored - kept for backward compatibility)                          |

## Error pages

For codes 400, 401, 403, 404, 405, 500, 502, 503, 504, 507 a handler is
registered that renders `errors/<code>.html`. For codes that are missing
from `werkzeug.exceptions.default_exceptions` (for example 507), an
`HTTPException` subclass is created automatically.

See [error-pages.md](error-pages.md).

## Returned HTTP codes

| Code | Meaning in the project                                                                |
|------|---------------------------------------------------------------------------------------|
| 200 | Successful template render                                                            |
| 302 | Redirect (after login/register/start/save/finish/publish)                             |
| 400 | Bad Request (form validation failed - usually a re-render with an alert, not a 400) |
| 401 | Not authorized - the guard redirects to `/login` (without an explicit 401)            |
| 403 | No permission (role does not match - redirect to `/dashboard`)                        |
| 404 | Resource not found - `abort(404)` for missing test/attempt/question                   |
| 405 | Method not allowed                                                                    |
| 500 | Internal error                                                                        |
