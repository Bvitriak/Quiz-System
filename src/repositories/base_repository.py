from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from src.models.base import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    model: Type[T]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, entity_id: int) -> Optional[T]:
        return self.db.get(self.model, entity_id)

    def add(self, entity: T) -> T:
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, entity: T) -> None:
        self.db.delete(entity)
        self.db.flush()
