import logging

from flask import Flask, g, jsonify, render_template, session
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.exceptions import HTTPException, default_exceptions

from src.blueprints import auth as auth_bp
from src.blueprints import student as student_bp
from src.blueprints import teacher as teacher_bp
from src.config import DEV_SECRET_KEY, settings
from src.database.connection import SessionLocal
from src.models import (  # pylint: disable=unused-import
    question,  # noqa: F401
    result,  # noqa: F401
    test,  # noqa: F401
    user,  # noqa: F401
)
from src.repositories.user_repository import RoleRepository, UserRepository
from src.utils.logging_config import configure_logging
from src.utils.rate_limit import limiter

log = logging.getLogger(__name__)
csrf = CSRFProtect()

def _check_production_secrets() -> None:
    if not settings.debug and settings.secret_key == DEV_SECRET_KEY:
        raise RuntimeError(
            "APP_SECRET_KEY uses the default value, "
            "which is not allowed in production. Set a unique key in .env."
        )

def _seed_default_roles() -> None:
    try:
        with SessionLocal() as db:
            RoleRepository(db).ensure_default()
            db.commit()
    except OperationalError as exc:
        log.error("Failed to connect to the database for role initialization: %s", exc)
    finally:
        SessionLocal.remove()


def create_app() -> Flask:
    configure_logging(
        level="DEBUG" if settings.debug else "INFO",
        log_file=settings.log_file,
    )
    _check_production_secrets()

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = settings.secret_key
    app.config.update(
        WTF_CSRF_TIME_LIMIT=None,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not settings.debug,
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,
    )

    csrf.init_app(app)
    limiter.init_app(app)
    _seed_default_roles()

    @app.route("/healthz")
    @csrf.exempt
    @limiter.exempt
    def healthz():
        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            status = "ok"
            code = 200
        except SQLAlchemyError as exc:
            log.error("Healthcheck failed: %s", exc)
            status = "db_error"
            code = 503
        finally:
            SessionLocal.remove()
        return jsonify(status=status), code

    @app.before_request
    def _open_db():
        g.db = SessionLocal()

    @app.after_request
    def _security_headers(response):
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; form-action 'self'; frame-ancestors 'none'",
        )
        if not settings.debug:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response

    @app.teardown_request
    def _close_db(exc):
        db = g.pop("db", None)
        if db is None:
            return
        try:
            if exc:
                db.rollback()
            else:
                db.commit()
        finally:
            SessionLocal.remove()

    @app.context_processor
    def inject_user():
        if not hasattr(g, "db"):
            return {"current_user": None, "admin_contact": settings.admin_contact}
        user_id = session.get("user_id")
        current_user = UserRepository(g.db).get(user_id) if user_id else None
        return {"current_user": current_user, "admin_contact": settings.admin_contact}

    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(student_bp.bp)
    app.register_blueprint(teacher_bp.bp)

    _register_error_handlers(app)
    return app

def _register_error_handlers(app: Flask) -> None:
    for code in (400, 401, 403, 404, 405, 500, 502, 503, 504, 507):
        if code not in default_exceptions:
            cls = type(
                f"HTTPError{code}",
                (HTTPException,),
                {"code": code, "description": f"HTTP {code}"},
            )
            default_exceptions[code] = cls

        def _handler(err, _code=code):
            log.warning("HTTP %s: %s", _code, err)
            return render_template(f"errors/{_code}.html"), _code

        app.register_error_handler(code, _handler)

    @app.errorhandler(OperationalError)
    def _db_error(exc):
        log.exception("Database error: %s", exc)
        return render_template("errors/503.html"), 503

def main() -> None:
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=settings.debug)

if __name__ == "__main__":
    main()
