import logging

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from src.blueprints.helpers import feedback_for, format_duration, quiz_ctrl
from src.config import settings
from src.utils.decorators import login_required

bp = Blueprint("student", __name__, url_prefix="/student")
log = logging.getLogger(__name__)

@bp.route("")
@login_required(role="student")
def index(user):
    quiz = quiz_ctrl()
    items = []
    for test_obj in quiz.list_tests():
        used = quiz.attempts_used(user.id, test_obj.id)
        left = (test_obj.max_attempts - used) if test_obj.max_attempts is not None else None
        last = (
            quiz.last_attempt(user.id, test_obj.id)
            if not quiz.can_start(user.id, test_obj)
            else None
        )
        items.append({
            "test": test_obj,
            "used": used,
            "left": left,
            "can_start": quiz.can_start(user.id, test_obj),
            "last_attempt": last,
        })
    return render_template(
        "student/tests.html",
        items=items,
        active_tab="tests",
        pass_threshold=settings.pass_threshold,
    )

@bp.route("/history")
@login_required(role="student")
def history(user):
    items = []
    quiz = quiz_ctrl()
    for attempt in quiz.history_for(user.id):
        test = quiz.get_test(attempt.test_id)
        if not test:
            continue
        items.append({
            "attempt": attempt,
            "test": test,
            "passed": attempt.success_percent >= settings.pass_threshold,
            "duration_text": format_duration(attempt.duration_seconds),
        })
    return render_template("student/history.html", items=items, active_tab="history")

def _require_attempt(quiz, user, attempt_id: int):
    attempt = quiz.get_attempt(attempt_id)
    if attempt is None or attempt.student_id != user.id:
        abort(404)
    return attempt

@bp.route("/tests/<int:test_id>/start", methods=["POST"])
@login_required(role="student")
def start_test(user, test_id):
    quiz = quiz_ctrl()
    try:
        attempt = quiz.start_attempt(user.id, test_id)
    except ValueError as exc:
        flash(str(exc), "error")
        last = quiz.last_attempt(user.id, test_id)
        if last and last.is_finished:
            return redirect(url_for("student.result", attempt_id=last.id))
        return redirect(url_for("student.index"))
    g.db.commit()
    log.info("Student id=%s started attempt id=%s of test id=%s",
             user.id, attempt.id, test_id)
    return redirect(url_for("student.question", attempt_id=attempt.id, n=1))

@bp.route("/attempts/<int:attempt_id>/question/<int:n>",
          methods=["GET", "POST"])
@login_required(role="student")
def question(user, attempt_id, n):
    quiz = quiz_ctrl()
    attempt = _require_attempt(quiz, user, attempt_id)
    if attempt.is_finished:
        return redirect(url_for("student.result", attempt_id=attempt.id))

    test = quiz.get_test(attempt.test_id)
    if test is None or n < 1 or n > test.question_count:
        abort(404)

    if quiz.remaining_seconds(attempt) <= 0:
        quiz.finish_attempt(attempt)
        flash("Time is up - attempt automatically finished", "info")
        return redirect(url_for(
            "student.result", attempt_id=attempt.id, auto=1
        ))

    questions = quiz.ordered_questions(attempt, test)
    current_q = questions[n - 1]

    if request.method == "POST":
        answered = False
        if current_q.question_type == "text":
            text_answer = request.form.get("text_answer", "").strip()
            if text_answer:
                quiz.save_text_answer(attempt, current_q, text_answer)
                answered = True
        elif current_q.question_type == "multiple":
            indexes = [int(v) for v in request.form.getlist("option") if v.isdigit()]
            if indexes:
                quiz.save_multi_answer(attempt, current_q, indexes)
                answered = True
        else:
            raw = request.form.get("option")
            if raw is not None and raw.isdigit():
                quiz.save_answer(attempt, current_q, int(raw))
                answered = True

        if not answered:
            flash("Select an answer to move on to the next question", "error")
            return redirect(url_for("student.question",
                                    attempt_id=attempt.id, n=n))
        if n < test.question_count:
            return redirect(url_for("student.question",
                                    attempt_id=attempt.id, n=n + 1))
        quiz.finish_attempt(attempt)
        log.info("Student id=%s finished attempt id=%s, result=%s%%",
                 user.id, attempt.id, attempt.success_percent)
        return redirect(url_for("student.result", attempt_id=attempt.id))

    return render_template(
        "student/test_take.html",
        attempt=attempt,
        test=test,
        questions=questions,
        question=current_q,
        current_index=n,
        remaining_seconds=quiz.remaining_seconds(attempt),
        active_tab="tests",
    )

@bp.route("/attempts/<int:attempt_id>/finish", methods=["POST"])
@login_required(role="student")
def finish(user, attempt_id):
    quiz = quiz_ctrl()
    attempt = _require_attempt(quiz, user, attempt_id)
    if not attempt.is_finished:
        quiz.finish_attempt(attempt)
        log.info("Student id=%s finished attempt id=%s, result=%s%%",
                 user.id, attempt.id, attempt.success_percent)
    return redirect(url_for("student.result", attempt_id=attempt.id))

@bp.route("/attempts/<int:attempt_id>/result")
@login_required(role="student")
def result(user, attempt_id):
    quiz = quiz_ctrl()
    attempt = _require_attempt(quiz, user, attempt_id)
    if not attempt.is_finished:
        return redirect(url_for("student.question",
                                attempt_id=attempt.id, n=1))
    test = quiz.get_test(attempt.test_id)
    if test is None:
        abort(404)
    auto_finished = request.args.get("auto") == "1"
    if not quiz.can_view_result(test):
        return render_template(
            "student/result_pending.html",
            test=test,
            attempt=attempt,
            auto_finished=auto_finished,
            active_tab="tests",
        )
    answers_by_qid = {a.question_id: a for a in attempt.answers_rel}
    correct_map = {qid: a.is_correct for qid, a in answers_by_qid.items()}
    return render_template(
        "student/result.html",
        attempt=attempt,
        test=test,
        questions=quiz.ordered_questions(attempt, test),
        passed=attempt.success_percent >= settings.pass_threshold,
        feedback=feedback_for(
            attempt.success_percent,
            settings.pass_threshold,
            settings.excellent_threshold,
        ),
        duration_text=format_duration(attempt.duration_seconds),
        correct_map=correct_map,
        answers_by_qid=answers_by_qid,
        active_tab="tests",
    )
