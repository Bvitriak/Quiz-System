# Authorization and roles

## Role model

The system has two roles - `student` and `teacher`. They are stored in the
`roles` table and seeded by migration 0008 (or by
`RoleRepository.ensure_default()` on the first run).

```python
class Role:
    CODE_STUDENT = "student"
    CODE_TEACHER = "teacher"
```

A user type is chosen ONCE - at registration time.
After that it cannot be changed (no UI; edit manually in the DB).

## Registration

`POST /register` → `AuthController.register()` → `AuthService.register()`.

1. **Validation** (`src/utils/validators.py`):
   - `email` is lowercased and checked against a regex
   - `password` - at least 8 characters, contains at least one letter and one digit
   - `password_confirm` equals `password`
   - `full_name` non-empty after `strip()`
   - `role` - {`student`, `teacher`}
2. **Duplicate check** for email in `users.email` (UNIQUE).
3. **Password hashing** via `bcrypt.hashpw(..., bcrypt.gensalt())`.
4. **Lookup `role_id`** via `RoleRepository.by_code()`.
5. **Create** a row in `users`.

Immediately after a successful registration `user_id` is placed in the
Flask session and the user is redirected based on role:
- `teacher` - `/teacher`
- `student` - `/student`

## Login

`POST /login` - `AuthService.login()`:

1. `validate_email` / `validate_password` (shallow format check).
2. `UserRepository.by_email()` - if `is_active=False` or the user does not exist - `ValueError("Invalid email or password")`.
3. `bcrypt.checkpw(...)` - hash comparison.
4. Success → `session["user_id"] = user.id`, redirect based on role.

On failure, the `auth/login.html` template is re-rendered with
`error="..."` shown in a red alert.

## Logout

`GET|POST /logout` - `session.pop("user_id", None)`. The cookie is cleared
on the browser side automatically.

## Sessions

**Flask session** is used (signed cookie on the client side).
`APP_SECRET_KEY` is taken from `.env`.

## Route protection

The decorators `login_required(role=…)` and `require_test_owner` live in
[`src/utils/decorators.py`](../../src/utils/decorators.py). The logic:

```python
def login_required(role: Optional[str] = None):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user_id = session.get("user_id")
            user = UserRepository(g.db).get(user_id) if user_id else None
            if user is None:
                return redirect(url_for("auth.login"))
            if role and user.role_code != role:
                return redirect(url_for("auth.dashboard"))
            return view(user, *args, **kwargs)
        return wrapper
    return decorator
```

`@require_test_owner` additionally verifies that `test_id` belongs to the
current user; otherwise - `404`.

Behavior:
- **Not logged in** - redirect to `/login`
- **Wrong role** - redirect to `/dashboard`
- The view function receives `user` (a `User` object) as the first argument.

## bcrypt: details

- The hash is stored **in UTF-8 encoding** (`hashpw(...).decode("utf-8")`).
- On check: `bcrypt.checkpw(password.encode(), user.password_hash.encode())`.
- Default cost factor (12 rounds).

## Tests

Relevant tests:
- [`tests/unit/test_auth_service.py`](../tests/unit/test_auth_service.py)
- [`tests/unit/test_validators.py`](../tests/unit/test_validators.py)
- [`tests/gui/test_auth_routes.py`](../tests/gui/test_auth_routes.py)
