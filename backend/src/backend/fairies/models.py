from sqlalchemy import Column, JSON
from sqlmodel import Field

from backend.database import Base


class Fairy(Base, table=True):
    __tablename__ = "fairies"

    name: str = Field(unique=True)
    prompt: str
    image_path: str
    image_content_type: str
    embeddings: list[float] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
