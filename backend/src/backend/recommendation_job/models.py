from datetime import datetime
from uuid import UUID
from sqlmodel import Field, Relationship
from backend.database import Base
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.fairies.models import Fairy


class RecommendationJob(Base, table=True):
    __tablename__ = "recommendation_jobs"

    user_id: UUID = Field(foreign_key="users.id")

    fairy_id: UUID = Field(foreign_key="fairies.id")
    fairy: "Fairy" = Relationship(back_populates="recommendation_jobs")
    latitude: float
    longitude: float
    start_date: datetime
    end_date: datetime
    budget: int

    status: "RecommendationStatus"


class RecommendationStatus(Enum):
    PENDING = "pending"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    FAILED = "failed"
