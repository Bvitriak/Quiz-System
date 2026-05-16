import re

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_VALID_ROLES = {"student", "teacher"}

def validate_email(email: str) -> str:
    email = (email or "").strip().lower()
    if not _EMAIL_RE.match(email):
        raise ValueError("Invalid Email")
    return email

_LETTER_RE = re.compile(r"[A-Za-z]")
_DIGIT_RE = re.compile(r"\d")

def validate_password(password: str) -> None:
    if not password or len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")
    if not _LETTER_RE.search(password):
        raise ValueError("Password must contain at least one letter")
    if not _DIGIT_RE.search(password):
        raise ValueError("Password must contain at least one digit")

def validate_role(role: str) -> str:
    role = (role or "").strip().lower()
    if role not in _VALID_ROLES:
        raise ValueError("Invalid role")
    return role
