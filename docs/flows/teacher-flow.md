# Teacher flow

After registration/login a teacher lands on `/teacher`.

## Screens

### `/teacher` - my tests

A table of all tests created by the current teacher
(`TestService.list_for_owner`). Columns:
- Title
- Number of questions
- Creation date
- Status (`Published` / `Draft`)
- Action: "Edit"

At the top - "Create test" button.

Template: [`teacher/tests.html`](../src/templates/teacher/tests.html).

### `/teacher/tests/new` - test creation

Form [`teacher/create.html`](../src/templates/teacher/create.html):

- Title, time limit (min), description, "Random order" flag
- Three question type cards:
  - "Single answer" → submit with `action=add:single`
  - "Multiple answers" → `add:multiple`
  - "Text answer" → `add:text`
- "Save as draft" and "Publish" buttons

Logic in `teacher_create`:
- If `action.startswith("add:")` → create the test and immediately redirect
  to the question add form with the chosen type.
- If `publish` - attempt to publish (will fail if there are no questions -
  then it remains a draft).
- Otherwise - `draft`, redirect to edit.

### `/teacher/tests/<id>/edit` - test configuration

Template [`teacher/edit.html`](../src/templates/teacher/edit.html):

- The same main parameters (title/limit/description/randomize)
- A grid of cards for existing questions:
  - Heading "Question N"
  - Icons: ✎ (edit link) and 🗑 (submit with
    `formaction=/questions/<qid>/delete`)
  - Body: radio/checkboxes (preview) or textarea placeholder
- At the bottom - a horizontal row of 4 buttons:
  "Add question" / "Availability settings" /
  "Save as draft" / "Publish"

### `/teacher/tests/<id>/questions/new` - add a question

Template [`teacher/question_new.html`](../src/templates/teacher/question_new.html)
is universal - it is used both for adding and for editing.

In add mode:
- Type switch `single` / `multiple` / `text` (radio chips)
- "Question text" field
- Options block (for single/multiple): at least 3 fields + a button
  "Add answer option" (JS adds new cards)
- For `text` - only the question text field (the reference answer was removed)

JS ([`teacher.js`](../src/static/teacher.js)):
- `initAnswers()` - handler for the "Add option" button, creates a new
  card with the correct `type` (radio / checkbox)
- `initTypeSwitch()` - on type change:
  - toggles the visibility of blocks (`data-roles`)
  - swaps radio↔checkbox on existing cards
  - removes excess checks when switching single → multiple

### `/teacher/tests/<id>/questions/<qid>/edit` - editing

The same template with pre-filled fields.
The type is fixed (`disabled` radio-buttons + a hidden field).
The button becomes "Save".

`TestService.update_question` rebuilds `options` and `text_answers`
from scratch (cleanup + append).

### `/teacher/tests/<id>/availability` - availability settings

Template [`teacher/availability.html`](../src/templates/teacher/availability.html):

- Start / end date and time (availability fields - currently kept in memory,
  there are no columns in the DB)
- Attempt count limit (`max_attempts` - **persisted in the DB**)
- "Show result immediately", "Random order" (also runtime)
- "Publish" / "Save" buttons

> **Note**. Of the four settings, only `max_attempts` and `shuffle_questions`
> (the latter exists in `tests`) are actually persisted. The rest are
> runtime model attributes. To persist them you need to add columns to
> `tests` via a migration (`availability_start`, `availability_end`,
> `show_result_immediately`).

### `/teacher/students` - student statistics

Template [`teacher/students.html`](../src/templates/teacher/students.html).
The table:
- Full name / email
- Number of attempts (only `finished`)
- Average `success_percent`
- Last attempt (date + score)

Logic - `TestService.student_stats(students)`.

## Related files

| Layer | File                                                                            |
|-------|---------------------------------------------------------------------------------|
| Service | [`src/services/test_service.py`](../src/services/test_service.py)               |
| Repository | [`src/repositories/test_repository.py`](../src/repositories/test_repository.py) |
| Routes | "Teacher" section in [`src/main.py`](../src/main.py)                            |
| Templates | [`src/templates/teacher/`](../src/templates/teacher/)                           |
| CSS | [`src/static/css/teacher.css`](../src/static/css/teacher.css)                   |
| JS | [`src/static/teacher.js`](../src/static/teacher.js)                             |
