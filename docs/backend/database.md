# Database

PostgreSQL 14+. The schema is described by the ORM models in [`src/models/`](../../src/models/);
the single source of truth is [Alembic migrations](migrations.md).

## Tables

### `roles`
| Column | Type | Description         |
|--------|------|---------------------|
| `id` | BIGSERIAL PK |                     |
| `code` | VARCHAR(255) UNIQUE | `student` or `teacher` |
| `name` | VARCHAR(255) | name                |

Seeded by migration [`0008`](migrations.md).

### `users`
| Column | Type | Description              |
|--------|------|--------------------------|
| `id` | BIGSERIAL PK |                          |
| `role_id` | BIGINT → `roles.id` | FK                       |
| `email` | VARCHAR(255) UNIQUE | normalized to lowercase  |
| `password_hash` | VARCHAR(255) | bcrypt                   |
| `full_name` | VARCHAR(255) |                          |
| `is_active` | BOOLEAN | `TRUE` by default        |
| `created_at` | TIMESTAMP | `NOW()`                  |

Index: `idx_users_email`.

### `sessions`
Placeholder for server-side sessions. The session is stored in Flask cookies.

### `tests`
| Column | Type | Description              |
|--------|------|--------------------------|
| `id` | BIGSERIAL PK |                          |
| `teacher_id` | BIGINT → `users.id` | author                   |
| `title` | VARCHAR(255) |                          |
| `description` | VARCHAR(255) |                          |
| `time_limit_minutes` | INT | attempt timer            |
| `status` | VARCHAR(255) | `draft` / `published`    |
| `shuffle_questions` | BOOLEAN | random order             |
| `created_at` | TIMESTAMP |                          |
| `published_at` | TIMESTAMP NULL |                          |
| `max_attempts` | INT NULL | attempt limit per student |

Indexes: `idx_tests_teacher`, `idx_tests_status`.

### `questions`
| Column | Type | Description                   |
|--------|------|-------------------------------|
| `id` | BIGSERIAL PK |                               |
| `test_id` | BIGINT → `tests.id` | ON DELETE CASCADE             |
| `question_type` | VARCHAR(255) | `single` / `multiple` / `text` |
| `text` | VARCHAR(255) |                               |
| `points` | INT | defaults to `1`               |
| `position` | INT | display order                 |

### `question_options`
Answer options for the `single` / `multiple` types.

| Column | Type | Description         |
|--------|------|---------------------|
| `id` | BIGSERIAL PK |                     |
| `question_id` | BIGINT → `questions.id` | ON DELETE CASCADE   |
| `option_text` | VARCHAR(255) |                     |
| `is_correct` | BOOLEAN | correctness flag    |
| `position` | INT | order               |

### `test_attempts`
One attempt at a test by a student.

| Column | Type | Description                              |
|--------|------|------------------------------------------|
| `id` | BIGSERIAL PK |                                          |
| `test_id` | BIGINT → `tests.id` |                                          |
| `student_id` | BIGINT → `users.id` |                                          |
| `attempt_no` | INT | attempt counter for the (student, test) pair |
| `status` | VARCHAR(255) | `in_progress` / `finished`               |
| `started_at` | TIMESTAMP |                                          |
| `finished_at` | TIMESTAMP NULL |                                          |
| `time_spent_seconds` | INT | computed in `finish_attempt`             |
| `score` | INT | sum of `awarded_points`                  |
| `success_percent` | INT | 0–100 (used in the UI)                   |
| `correct_answers_count` | INT |                                          |

### `attempt_answers`
A student's answer to one question within an attempt.

| Column | Type | Description                 |
|--------|------|-----------------------------|
| `id` | BIGSERIAL PK |                             |
| `attempt_id` | BIGINT → `test_attempts.id` | ON DELETE CASCADE           |
| `question_id` | BIGINT → `questions.id` |                             |
| `question_order_shown` | INT | for `shuffle_questions`     |
| `text_answer_raw` | VARCHAR(255) | original text input         |
| `text_answer_normalized` | VARCHAR(255) | lowercase + single-space    |
| `is_correct` | BOOLEAN |                             |
| `awarded_points` | INT |                             |

### `attempt_answer_options`
Which options the student picked (for single/multiple).

| Column | Type | Description         |
|--------|------|---------------------|
| `id` | BIGSERIAL PK |                     |
| `attempt_answer_id` | BIGINT → `attempt_answers.id` | ON DELETE CASCADE   |
| `option_id` | BIGINT → `question_options.id` |                     |
| `option_order_shown` | INT |                     |

### `test_status_history`
History of test status changes (created for audit; not currently written to in this version).

## Indexes

```sql
CREATE INDEX idx_users_email         ON users(email);
CREATE INDEX idx_sessions_token      ON sessions(session_token);
CREATE INDEX idx_tests_teacher       ON tests(teacher_id);
CREATE INDEX idx_tests_status        ON tests(status);
CREATE INDEX idx_questions_test      ON questions(test_id);
CREATE INDEX idx_options_question    ON question_options(question_id);
CREATE INDEX idx_attempts_student    ON test_attempts(student_id);
CREATE INDEX idx_attempts_test       ON test_attempts(test_id);
CREATE INDEX idx_answers_attempt     ON attempt_answers(attempt_id);
CREATE INDEX idx_answer_opts_answer  ON attempt_answer_options(attempt_answer_id);
```

## Cascade deletes

- `tests` deleted - cascades delete `questions`, `test_status_history`
- `questions` deleted - cascades `question_options`, `question_text_answers`
- `test_attempts` deleted - cascades `attempt_answers`
- `attempt_answers` deleted - cascades `attempt_answer_options`
- `users` deleted - cascades `sessions`

`test_attempts` are NOT cascaded when a user is deleted (history is preserved).

## SQLAlchemy models

Model files:
- [`src/models/user.py`](../src/models/user.py) - `Role`, `User`, `SessionToken`
- [`src/models/test.py`](../src/models/test.py) - `Test`, `TestStatusHistory`
- [`src/models/question.py`](../src/models/question.py) - `Question`, `QuestionOption`, `QuestionTextAnswer`
- [`src/models/result.py`](../src/models/result.py) - `TestAttempt`, `AttemptAnswer`, `AttemptAnswerOption`
