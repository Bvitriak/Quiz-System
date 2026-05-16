from unittest.mock import MagicMock
import bcrypt
import pytest
from src.services.auth_service import AuthService

def _make_service(role_lookup=None, by_email=None):
    users = MagicMock()
    users.by_email.return_value = by_email
    roles = MagicMock()
    roles.by_code.return_value = role_lookup
    return AuthService(users, roles), users, roles

def test_register_creates_user_with_hashed_password():
    role = MagicMock(id=1)
    svc, users, _ = _make_service(role_lookup=role, by_email=None)

    user = svc.register("a@b.io", "secret123", "Anna", "student")

    users.add.assert_called_once()
    assert user.email == "a@b.io"
    assert user.full_name == "Anna"
    assert user.role_id == 1
    assert bcrypt.checkpw(b"secret123", user.password_hash.encode())

def test_register_duplicate_email_raises():
    existing = MagicMock()
    svc, _, _ = _make_service(role_lookup=MagicMock(id=1), by_email=existing)

    with pytest.raises(ValueError, match="already exists"):
        svc.register("a@b.io", "secret123", "Anna", "student")

def test_register_unknown_role_raises():
    svc, _, _ = _make_service(role_lookup=None, by_email=None)

    with pytest.raises(ValueError, match="Role not found"):
        svc.register("a@b.io", "secret123", "Anna", "student")

def test_login_wrong_password_raises():
    user = MagicMock(
        is_active=True,
        password_hash=bcrypt.hashpw(b"right", bcrypt.gensalt()).decode(),
    )
    svc, _, _ = _make_service(by_email=user)

    with pytest.raises(ValueError):
        svc.login("a@b.io", "wrong")

def test_login_inactive_raises():
    user = MagicMock(is_active=False)
    svc, _, _ = _make_service(by_email=user)
    with pytest.raises(ValueError):
        svc.login("a@b.io", "any")

def test_login_success_returns_user():
    user = MagicMock(
        is_active=True,
        password_hash=bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode(),
    )
    svc, _, _ = _make_service(by_email=user)
    assert svc.login("a@b.io", "secret") is user

def test_get_by_id_none_when_zero():
    svc, users, _ = _make_service()
    assert svc.get_by_id(0) is None
    users.get.assert_not_called()

def test_list_by_role_delegates():
    svc, users, _ = _make_service()
    users.list_by_role_code.return_value = ["a", "b"]
    assert svc.list_by_role("student") == ["a", "b"]
    users.list_by_role_code.assert_called_with("student")
