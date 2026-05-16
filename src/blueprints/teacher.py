import logging

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from src.blueprints.helpers import auth_ctrl, parse_dt, test_ctrl
from src.utils.decorators import login_required, require_test_owner

bp = Blueprint("teacher", __name__, url_prefix="/teacher")
log = logging.getLogger(__name__)

@bp.route("")
@login_required(role="teacher")
def index(user):
    return render_template(
        "teacher/tests.html",
        tests=test_ctrl().list_for_owner(user.id),
        active_tab="tests",
    )

@bp.route("/students")
@login_required(role="teacher")
def students(user):
    student_users = auth_ctrl().list_by_role("student")
    return render_template(
        "teacher/students.html",
        rows=test_ctrl().student_stats(student_users),
        active_tab="students",
    )

@bp.route("/tests/new", methods=["GET", "POST"])
@login_required(role="teacher")
def create(user):
    tc = test_ctrl()
    if request.method == "POST":
        try:
            test = tc.create(
                owner_id=user.id,
                title=request.form.get("title", ""),
                time_limit_minutes=int(request.form.get("time_limit_minutes") or 0),
                description=request.form.get("description", ""),
                randomize=bool(request.form.get("randomize")),
            )
        except (ValueError, TypeError) as exc:
            return render_template("teacher/create.html", active_tab="tests", error=str(exc))

        g.db.commit()
        log.info("Teacher id=%s created test id=%s", user.id, test.id)
        action = request.form.get("action", "draft")
        if action.startswith("add:"):
            qtype = action.split(":", 1)[1]
            return redirect(url_for("teacher.add_question", test_id=test.id, type=qtype))
        if action == "publish":
            try:
                tc.publish(test, changed_by=user.id)
                flash("Test published", "success")
            except ValueError as exc:
                flash(str(exc), "error")
            return redirect(url_for("teacher.index"))
        flash("Draft saved", "success")
        return redirect(url_for("teacher.index"))

    return render_template("teacher/create.html", active_tab="tests")

@bp.route("/tests/<int:test_id>/edit", methods=["GET", "POST"])
@login_required(role="teacher")
@require_test_owner
def edit(user, test_id, test):
    from src.models.test import STATUS_PUBLISHED
    tc = test_ctrl()
    error = None
    if request.method == "POST":
        action = request.form.get("action", "draft")
        try:
            if action == "draft" and test.status == STATUS_PUBLISHED:
                tc.to_draft(test, changed_by=user.id)
                flash("Test moved to draft", "success")
            else:
                tc.update_basics(
                    test,
                    title=request.form.get("title", ""),
                    time_limit_minutes=int(request.form.get("time_limit_minutes") or 0),
                    description=request.form.get("description", ""),
                    randomize=bool(request.form.get("randomize")),
                )
                if action == "publish":
                    tc.publish(test, changed_by=user.id)
                    flash("Test published", "success")
                elif action == "draft":
                    tc.to_draft(test, changed_by=user.id)
                    flash("Test moved to draft", "success")
                else:
                    flash("Changes saved", "success")
        except (ValueError, TypeError) as exc:
            error = str(exc)
        else:
            if action in ("publish", "draft"):
                return redirect(url_for("teacher.index"))
            return redirect(url_for("teacher.edit", test_id=test.id))
    return render_template("teacher/edit.html", test=test, active_tab="tests", error=error)

@bp.route("/tests/<int:test_id>/questions/new", methods=["GET", "POST"])
@login_required(role="teacher")
@require_test_owner
def add_question(user, test_id, test):
    tc = test_ctrl()
    qtype = request.values.get("type", "single")
    form_action = url_for("teacher.add_question", test_id=test.id, type=qtype)

    if request.method == "POST" and "text" in request.form:
        try:
            points_raw = (request.form.get("points") or "1").strip()
            try:
                points_val = int(points_raw)
            except ValueError as exc:
                raise ValueError("Score must be an integer") from exc
            tc.add_question(
                test,
                qtype=request.form.get("type", qtype),
                text=request.form.get("text", ""),
                options=request.form.getlist("option"),
                correct_indexes=[
                    int(i) for i in request.form.getlist("correct") if i.isdigit()
                ],
                correct_text=request.form.get("correct_text", ""),
                points=points_val,
            )
        except ValueError as exc:
            return render_template(
                "teacher/question_new.html",
                test=test, qtype=qtype, active_tab="tests",
                form_action=form_action,
                page_title="Add question",
                error=str(exc),
            )
        flash("Question added", "success")
        return redirect(url_for("teacher.edit", test_id=test.id))

    return render_template(
        "teacher/question_new.html",
        test=test, qtype=qtype, active_tab="tests",
        form_action=form_action,
        page_title="Add question",
    )

@bp.route(
    "/tests/<int:test_id>/questions/<int:question_id>/edit",
    methods=["GET", "POST"],
)
@login_required(role="teacher")
@require_test_owner
def edit_question(user, test_id, question_id, test):
    tc = test_ctrl()
    question = tc.get_question(test, question_id)
    if question is None:
        abort(404)
    qtype = question.question_type
    form_action = url_for(
        "teacher.edit_question", test_id=test.id, question_id=question.id
    )

    if request.method == "POST":
        try:
            points_raw = (request.form.get("points") or "").strip()
            tc.update_question(
                question,
                text=request.form.get("text", ""),
                options=request.form.getlist("option"),
                correct_indexes=[
                    int(i) for i in request.form.getlist("correct") if i.isdigit()
                ],
                correct_text=request.form.get("correct_text", ""),
                points=int(points_raw) if points_raw else None,
            )
        except ValueError as exc:
            return render_template(
                "teacher/question_new.html",
                test=test, question=question, qtype=qtype,
                active_tab="tests",
                form_action=form_action,
                page_title="Edit question",
                error=str(exc),
            )
        flash("Question updated", "success")
        return redirect(url_for("teacher.edit", test_id=test.id))

    return render_template(
        "teacher/question_new.html",
        test=test, question=question, qtype=qtype,
        active_tab="tests",
        form_action=form_action,
        page_title="Edit question",
    )

@bp.route("/tests/<int:test_id>/questions/<int:question_id>/delete",
          methods=["POST"])
@login_required(role="teacher")
@require_test_owner
def delete_question(user, test_id, question_id, test):
    try:
        test_ctrl().delete_question(test, question_id)
    except ValueError as exc:
        flash(str(exc), "error")
    else:
        flash("Question deleted", "success")
    return redirect(url_for("teacher.edit", test_id=test.id))

@bp.route("/tests/<int:test_id>/delete", methods=["POST"])
@login_required(role="teacher")
@require_test_owner
def delete(user, test_id, test):
    try:
        test_ctrl().delete(test)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("teacher.edit", test_id=test_id))
    flash("Test deleted", "success")
    return redirect(url_for("teacher.index"))

@bp.route("/tests/<int:test_id>/availability", methods=["GET", "POST"])
@login_required(role="teacher")
@require_test_owner
def availability(user, test_id, test):
    tc = test_ctrl()
    error = None
    if request.method == "POST":
        max_attempts_raw = (request.form.get("max_attempts") or "").strip()
        time_limit_raw = (request.form.get("time_limit_minutes") or "").strip()
        try:
            max_attempts = int(max_attempts_raw) if max_attempts_raw else None
            time_limit_minutes = int(time_limit_raw) if time_limit_raw else None
            tc.update_availability(
                test,
                start=parse_dt(request.form.get("start_date", ""),
                               request.form.get("start_time", "")),
                end=parse_dt(request.form.get("end_date", ""),
                             request.form.get("end_time", "")),
                max_attempts=max_attempts,
                show_result_immediately=bool(request.form.get("show_result_immediately")),
                randomize=test.shuffle_questions,
                time_limit_minutes=time_limit_minutes,
            )
            if request.form.get("action") == "publish":
                tc.publish(test, changed_by=user.id)
                flash("Test published", "success")
            else:
                flash("Availability settings saved", "success")
        except (ValueError, TypeError) as exc:
            error = str(exc)
        else:
            return redirect(url_for("teacher.edit", test_id=test.id))
    return render_template("teacher/availability.html", test=test,
                           active_tab="tests", error=error)
