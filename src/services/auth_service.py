from typing import Optional

import bcrypt
from sqlalchemy.exc import IntegrityError

from src.models.user import User
from src.repositories.user_repository import RoleRepository, UserRepository
from src.utils.validators import validate_role


class AuthService:
    def __init__(self, users: UserRepository, roles: RoleRepository) -> None:
        self._users = users
        self._roles = roles

    def get_by_id(self, user_id: int) -> Optional[User]:
        if not user_id:
            return None
        return self._users.get(user_id)

    def by_email(self, email: str) -> Optional[User]:
        return self._users.by_email(email)

    def list_by_role(self, role_code: str) -> list[User]:
        return self._users.list_by_role_code(role_code)

    def register(self, email: str, password: str, full_name: str, role: str) -> User:
        role_code = validate_role(role)
        if self._users.by_email(email):
            raise ValueError("A user with this Email already exists")
        role_row = self._roles.by_code(role_code)
        if role_row is None:
            raise ValueError("Role not found in the database")
        user = User(
            email=email,
            password_hash=bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            full_name=full_name.strip(),
            role_id=role_row.id,
            is_active=True,
        )
        try:
            self._users.add(user)
        except IntegrityError as exc:
            self._users.db.rollback()
            raise ValueError(
                "A user with this Email already exists"
            ) from exc
        return user

    def login(self, email: str, password: str) -> User:
        user = self._users.by_email(email)
        if user is None or not user.is_active:
            raise ValueError("Invalid Email or password")
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            raise ValueError("Invalid Email or password")
        return user

    def logout(self) -> None:
        return
