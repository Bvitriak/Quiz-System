from functools import wraps
from typing import Optional

from flask import abort, g, redirect, session, url_for

from src.repositories.test_repository import TestRepository
from src.repositories.user_repository import UserRepository


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

def require_test_owner(view):
    @wraps(view)
    def wrapper(user, *args, **kwargs):
        test_id = kwargs.get("test_id")
        if test_id is None:
            abort(404)
        test = TestRepository(g.db).get(test_id)
        if test is None or test.teacher_id != user.id:
            abort(404)
        kwargs["test"] = test
        return view(user, *args, **kwargs)

    return wrapper
