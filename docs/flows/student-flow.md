# Student flow

After registration/login a student lands on `/student`.

## Steps

### 1. `/student` - list of available tests

- Only tests with `status="published"` are shown (filter in
  `TestRepository.list_published`).
- Each card shows: title, deadline, number of questions, time limit.
- If the test has `max_attempts` set and it is exhausted - the
  "Start test" button is replaced by "Limit reached - view result"
  (a link to the result of the last attempt).
- The `Attempts: used / max` counter is shown only if the limit is set.

Template: [`student/tests.html`](../src/templates/student/tests.html).

### 2. `POST /student/tests/<id>/start` - start the test

- `QuizService.start_attempt()`:
  - Verifies the test exists.
  - Checks `can_start` (attempt limit not exceeded).
  - Creates a `TestAttempt` with `attempt_no = used + 1`, `started_at = now`,
    `status = "in_progress"`.
- On error (limit) - redirect to the result of the last attempt or
  back to `/student`.

### 3. `/student/attempts/<aid>/question/<n>` - taking the test

GET renders [`student/test_take.html`](../src/templates/student/test_take.html):

- Header: "Question N/M", countdown timer
- Body: depends on `question.type`:
  - `single` - radio buttons
  - `multiple` - checkboxes
  - `text` - textarea
- Sidebar: info card (total questions, remaining time, progress) +
  question navigation (click a number to jump to that question)
- Buttons: "Finish" (formaction - `/finish`) and "Next"

POST:
- If `question.type == "text"` - `QuizService.save_text_answer`
- Otherwise - `QuizService.save_answer` (with the index of the chosen option)
- Redirect to `/question/<n+1>` or `/finish` (if it is the last one)

**Timer** ([`student.js`](../src/static/student.js)):
- Reads `data-remaining` from the form (seconds until deadline)
- Every second updates `#timer` and `#timerInfo`
- At `0` submits an auto-finish via the hidden form at `data-timeout-url`

### 4. `POST /student/attempts/<aid>/finish` - finish

`QuizService.finish_attempt`:
- `finished_at = now`, `status = "finished"`, `time_spent_seconds`
- For each question:
  - `single` / `multiple`: `is_correct = set(selected) == set(correct)`
  - `text`: `is_correct = bool(non-empty text_answer_raw)`
- `score = sum(awarded_points)`
- `success_percent = round(total / max_points * 100)`
- `correct_answers_count`

### 5. `/student/attempts/<aid>/result` - result

[`student/result.html`](../src/templates/student/result.html):

- **Top block**: `success_percent / 100`, "Test passed / Not passed" badge,
  correct answers, motivational phrase based on the result, time spent.
- **Sidebar**: info card + navigation (green/red numbers).
- **Answer breakdown**: list of all questions with a colored bar
  (green - correct, red - incorrect):
  - For `single`/`multiple` - all options with ✓/✗ markers + a "your answer" tag
  - For `text` - "Your answer" (if any)

### 6. `/student/history` - history

All attempts by the student (most recent first). For each:
- Test title, date, `success_percent`, status, attempt number, duration,
  "Open" button - to the result page.

Template: [`student/history.html`](../src/templates/student/history.html).

## "Passed" threshold

`success_percent >= PASS_THRESHOLD` (60 by default - from `.env`).
The "Test passed" badge and the message in history depend on this.

## Attempt limit

If `tests.max_attempts is not None`, attempts are counted via
`TestAttemptRepository.count_for_user_test`. When `used >= max_attempts`:
- The card on `/student` shows an alternative button
- `POST /tests/<id>/start` raises `ValueError("Attempt limit reached")`
  and redirects to the result of the last attempt

## Related files

| Layer | File                                                                                |
|-------|-------------------------------------------------------------------------------------|
| Service | [`src/services/quiz_service.py`](../src/services/quiz_service.py)                   |
| Repositories | [`src/repositories/result_repository.py`](../src/repositories/result_repository.py) |
| Routes | "Student" section in [`src/main.py`](../src/main.py)                                |
| Templates | [`src/templates/student/`](../src/templates/student/)                               |
| CSS | [`src/static/css/student.css`](../src/static/css/student.css)                       |
| JS | [`src/static/student.js`](../src/static/student.js)                                 |
