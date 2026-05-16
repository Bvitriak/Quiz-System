from typing import Optional

from sqlalchemy import select

from src.models.user import Role, User
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_role_code(self, code: str) -> list[User]:
        stmt = (
            select(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.code == code)
            .order_by(User.full_name)
        )
        return list(self.db.execute(stmt).scalars())

class RoleRepository(BaseRepository[Role]):
    model = Role

    def by_code(self, code: str) -> Optional[Role]:
        return self.db.execute(
            select(Role).where(Role.code == code)
        ).scalar_one_or_none()

    def ensure_default(self) -> None:
        for code, name in (("student", "Student"), ("teacher", "Teacher")):
            if self.by_code(code) is None:
                self.db.add(Role(code=code, name=name))
        self.db.flush()
