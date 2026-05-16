from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from src.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
    echo=settings.debug,
)

SessionLocal = scoped_session(  # pylint: disable=invalid-name
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)

@contextmanager
def session_scope() -> Iterator[Session]:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        SessionLocal.remove()

def get_session() -> Session:
    return SessionLocal()
