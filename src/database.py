import os
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from . import model

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/TaskFlow",
)
engine = create_engine(DATABASE_URL)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session