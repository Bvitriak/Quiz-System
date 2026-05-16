import logging

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from src.blueprints.helpers import auth_ctrl, redirect_for_role
from src.config import settings
from src.repositories.user_repository import UserRepository
from src.utils.rate_limit import limiter

bp = Blueprint("auth", __name__)
log = logging.getLogger(__name__)

@bp.route("/")
def index():
    user_id = session.get("user_id")
    if user_id and UserRepository(g.db).get(user_id):
        return redirect(url_for("auth.dashboard"))
    return render_template("auth/index.html")

@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def register():
    error = None
    if request.method == "POST":
        try:
            user = auth_ctrl().register(
                email=request.form.get("email", ""),
                password=request.form.get("password", ""),
                password_confirm=request.form.get("password_confirm", ""),
                full_name=request.form.get("full_name", ""),
                role=request.form.get("role", ""),
            )
        except ValueError as exc:
            error = str(exc)
        else:
            g.db.commit()
            session["user_id"] = user.id
            log.info("Registered user id=%s role=%s", user.id, user.role_code)
            flash("Account created successfully", "success")
            return redirect_for_role(user)
    return render_template("auth/register.html", error=error)

@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per 15 minutes", methods=["POST"])
def login():
    error = None
    if request.method == "POST":
        try:
            user = auth_ctrl().login(
                email=request.form.get("email", ""),
                password=request.form.get("password", ""),
            )
        except ValueError as exc:
            error = str(exc)
        else:
            session["user_id"] = user.id
            log.info("User signed in id=%s", user.id)
            flash("You have signed in", "success")
            return redirect_for_role(user)
    return render_template("auth/login.html", error=error)

@bp.route("/logout", methods=["POST", "GET"])
def logout():
    user_id = session.pop("user_id", None)
    if user_id:
        log.info("User logged out id=%s", user_id)
        flash("You have logged out", "info")
    return redirect(url_for("auth.index"))

@bp.route("/forgot-password")
@limiter.limit("20 per hour")
def forgot_password():
    return render_template(
        "auth/forgot_password.html",
        admin_contact=settings.admin_contact,
    )

@bp.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    user = UserRepository(g.db).get(user_id) if user_id else None
    if user is None:
        return redirect(url_for("auth.login"))
    return redirect_for_role(user)
