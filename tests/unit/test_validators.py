import pytest
from src.utils.validators import validate_email, validate_password, validate_role

class TestValidateEmail:
    def test_valid_email_lowercased(self):
        assert validate_email("Foo@Example.COM") == "foo@example.com"

    def test_strips_whitespace(self):
        assert validate_email("  user@x.io  ") == "user@x.io"

    @pytest.mark.parametrize("bad", ["", "noatsign", "a@b", "a@b.", "@b.io", "a b@c.io"])
    def test_invalid(self, bad):
        with pytest.raises(ValueError):
            validate_email(bad)

class TestValidatePassword:
    def test_ok(self):
        validate_password("strong123")

    @pytest.mark.parametrize("bad", ["", "12345", "abcde", "short1"])
    def test_too_short(self, bad):
        with pytest.raises(ValueError, match="at least"):
            validate_password(bad)

    def test_letters_only_rejected(self):
        with pytest.raises(ValueError, match="digit"):
            validate_password("abcdefgh")

    def test_digits_only_rejected(self):
        with pytest.raises(ValueError, match="letter"):
            validate_password("12345678")

class TestValidateRole:
    @pytest.mark.parametrize("role", ["student", "teacher", "STUDENT", "Teacher"])
    def test_ok(self, role):
        assert validate_role(role) in {"student", "teacher"}

    @pytest.mark.parametrize("bad", ["", "admin", "pupil", None])
    def test_invalid(self, bad):
        with pytest.raises(ValueError):
            validate_role(bad)
