from collections.abc import Generator
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Session, SQLModel, create_engine

from backend.config import settings

engine = create_engine(
    settings.SQLMODEL_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)


def get_db_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


class Base(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
