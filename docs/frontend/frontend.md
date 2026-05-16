# Templates and styles

## `templates/` structure

```
src/templates/
├── auth/                    - public pages
│   ├── index.html           - landing page
│   ├── login.html
│   └── register.html
├── student/                 - student area
│   ├── _base.html           - layout with topbar
│   ├── tests.html
│   ├── test_take.html
│   ├── result.html
│   └── history.html
├── teacher/                 - teacher area
│   ├── _base.html
│   ├── tests.html
│   ├── create.html
│   ├── edit.html
│   ├── question_new.html
│   ├── availability.html
│   └── students.html
└── errors/                  - error pages
    ├── _base.html
    └── 400.html / 401.html / 403.html / 404.html / 405.html
      / 500.html / 502.html / 503.html / 504.html / 507.html
```

`_base.html` in each section contains `<head>`, the topbar and
`{% block content %}` / `{% block scripts %}` blocks.

## `static/` structure

```
src/static/
├── css/
│   ├── auth.css       - common variables, forms, buttons
│   ├── student.css    - topbar, tables, transitions, answer review
│   ├── teacher.css    - question cards, type switcher
│   └── errors.css     - styling of error pages
├── auth.js            - client-side validation for login/register forms
├── student.js         - countdown timer
├── teacher.js         - question type switcher, +answer option
├── topbar.js          - user dropdown menu, transitions between pages
└── errors.js          - "Back" button
```

## Design system

CSS variables are defined in [`auth.css`](../src/static/css/auth.css):

| Variable | Value | Usage                  |
|----------|-------|------------------------|
| `--color-bg` | `#eef1f5` | page background        |
| `--color-card` | `#dbe6f3` | cards and panels       |
| `--color-input-bg` | `#f5f8fc` | input field background |
| `--color-border` | `#c5d4e8` | borders                |
| `--color-primary` | `#4a7ec1` | primary blue           |
| `--color-primary-hover` | `#3d6cab` | hover                  |
| `--color-text` | `#14375e` | main text              |
| `--color-text-muted` | `#5f7691` | captions               |
| `--color-danger` | `#c0392b` | errors and wrong answers |
| `--radius-card` | `18px` | card border radius     |
| `--radius-input` | `14px` | input border radius    |
| `--radius-button` | `14px` | button border radius   |

## Topbar

Identical structure in `student/_base.html` and `teacher/_base.html`:

- Left - logo (`Q` inside a circle + the text `uiz` + `system`)
- Center - tabs (role-dependent: "Tests/Attempts" or "Tests/Students")
- Right - avatar with the first letter of the name. Clicking it opens a
  dropdown menu with the full name, role and a "Log out" button. It is
  closed by clicking outside, by Escape, or by clicking the avatar again.

JS - [`topbar.js`](../src/static/topbar.js).

## Transitions between pages

Implemented with two layers:

1. **View Transitions API** (Chrome 126+):
   ```html
   <meta name="view-transition" content="same-origin">
   ```
   The CSS section `@supports (view-transition-name: none)` assigns the
   `::view-transition-old(root)` (fade-out) and `::view-transition-new(root)`
   (fade-in) animations. `.topbar` gets `view-transition-name: app-topbar`
   so it does not flicker together with the whole page.

2. **JS fallback** (`topbar.js → initPageTransitions`):
   - Intercepts clicks on `.tabs__item`, `.topbar__logo`,
     `.user-menu__logout`.
   - Adds `body.is-leaving` → fade-out 170 ms.
   - After that - `window.location.href = href`.
   - When navigating back (`pageshow`) the class is reset.

`prefers-reduced-motion: reduce` is respected - animations are disabled.

## JS on the page

| File | When included | Purpose                       |
|------|---------------|-------------------------------|
| `topbar.js` | everywhere with a topbar | menu + transitions            |
| `auth.js` | login/register | client-side form validation   |
| `student.js` | test-taking page | countdown timer               |
| `teacher.js` | question forms | type switcher + options       |
| `errors.js` | error pages | "Back" button                 |

## Jinja details

- All static links go through `{{ url_for('static', filename='...') }}`.
- `current_user` is injected via `app.context_processor`:
  ```python
  @app.context_processor
  def inject_user():
      user_id = session.get("user_id")
      user = UserRepository(g.db).get(user_id) if user_id else None
      return {"current_user": user}
  ```
- In the 4xx/5xx error templates `current_user` is also available,
  but is not used - error pages are isolated from the topbar.

## Accessibility (A11Y)

Supported:
- Topbar dropdown menu - `aria-haspopup`, `aria-expanded`, `aria-controls`,
  `role="menu"`.
- The menu closes on `Escape`, focus returns to the avatar.
- `prefers-reduced-motion: reduce` disables all animations.
- Form fields have `placeholder` and the required `type=email/number/date/time`.
- Buttons that play a form role have `type="submit"` or
  `type="button"` set explicitly.
