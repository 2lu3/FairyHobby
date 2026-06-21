from typing import TYPE_CHECKING

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship

from backend.database import Base

if TYPE_CHECKING:
    from backend.recommendation_job.models import RecommendationJob


class Fairy(Base, table=True):
    __tablename__ = "fairies"

    name: str = Field(unique=True)
    prompt: str
    image_path: str
    image_content_type: str
    embeddings: list[float] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )

    recommendation_jobs: list["RecommendationJob"] = Relationship(
        back_populates="fairy"
    )
