import os
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@database:5432/music_library"
)

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency. Stays a generator so `Depends(get_session)` works."""
    with Session(engine) as session:
        yield session


# Context-manager form for scripts / non-request code (seed, one-offs):
#   with session_scope() as session: ...
session_scope = contextmanager(get_session)
