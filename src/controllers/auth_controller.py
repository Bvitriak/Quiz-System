from src.models.user import User
from src.services.auth_service import AuthService
from src.utils.validators import validate_email, validate_password, validate_role


class AuthController:
    def __init__(self, auth_service: AuthService) -> None:
        self._service = auth_service

    def list_by_role(self, role_code: str) -> list[User]:
        return self._service.list_by_role(role_code)

    def login(self, email: str, password: str) -> User:
        email = validate_email(email)
        validate_password(password)
        return self._service.login(email, password)

    def logout(self) -> None:
        self._service.logout()

    def register(
        self,
        email: str,
        password: str,
        password_confirm: str,
        full_name: str,
        role: str,
    ) -> User:
        email = validate_email(email)
        validate_password(password)
        if password != password_confirm:
            raise ValueError("Passwords do not match")
        if not full_name.strip():
            raise ValueError("Name cannot be empty")
        role = validate_role(role)
        return self._service.register(email, password, full_name, role)
