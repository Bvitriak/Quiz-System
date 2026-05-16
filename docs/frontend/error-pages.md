# Error pages

For all "major" HTTP errors a handler is registered in Flask
that renders the `errors/<code>.html` template.

## Supported codes

| Code | Template heading | When it happens                                           |
|------|------------------|-----------------------------------------------------------|
| 400 | Bad Request | malformed form data                                       |
| 401 | Authorization required | (reserved - usually the guard redirects to /login)        |
| 403 | Forbidden | (reserved - the role guard uses a redirect)               |
| 404 | Page not found | `abort(404)` for a missing test/attempt/question          |
| 405 | Method not allowed | GET to a POST-only route                                  |
| 500 | Internal Server Error | unhandled exception                                       |
| 502 | Bad Gateway | (proxy scenarios)                                         |
| 503 | Service Unavailable | (maintenance)                                             |
| 504 | Gateway Timeout | (upstream timeout)                                        |
| 507 | Insufficient Storage | (placeholder for production)                              |

## Registration

In [`src/main.py`](../src/main.py):

```python
from werkzeug.exceptions import HTTPException, default_exceptions

for code in (400, 401, 403, 404, 405, 500, 502, 503, 504, 507):
    if code not in default_exceptions:
        cls = type(
            f"HTTPError{code}",
            (HTTPException,),
            {"code": code, "description": f"HTTP {code}"},
        )
        default_exceptions[code] = cls

    def _handler(err, _code=code):
        return render_template(f"errors/{_code}.html"), _code
    app.register_error_handler(code, _handler)
```

For codes that are missing from `werkzeug.exceptions.default_exceptions`
(for example `507`), an `HTTPException` subclass is created on the fly.

## Templates

All of them inherit [`errors/_base.html`](../src/templates/errors/_base.html),
which takes three variables via `{% set %}`:

```jinja
{% set code = 404 %}
{% set title = "Page not found" %}
{% set description = "The requested page does not exist..." %}
```

The `_base.html` layout:
- Includes `auth.css` and `errors.css`
- Large error code with an appearance animation
- Heading and description
- "Home" and "Back" buttons
- Includes `errors.js`

## Styles

[`src/static/css/errors.css`](../src/static/css/errors.css):
- A `.error` card centred on the screen
- `@keyframes error-pop` animation for the large code digits
- Different colors for 4xx (yellow-orange) and 5xx (red)
- Responsive sizes for `max-width: 480px`

## JS

[`src/static/errors.js`](../src/static/errors.js) - handles the
"Back" button: calls `history.back()` or redirects to `/` if there is no history.
