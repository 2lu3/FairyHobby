from datetime import date
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.types import Enum as SAEnum
from sqlmodel import Column, Field, Relationship

from backend.database import Base

if TYPE_CHECKING:
    from backend.fairies.models import Fairy


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    FAILED = "failed"


class RecommendationJob(Base, table=True):
    __tablename__ = "recommendation_jobs"

    user_id: UUID = Field(foreign_key="users.id")

    fairy_id: UUID = Field(foreign_key="fairies.id")
    fairy: "Fairy" = Relationship(back_populates="recommendation_jobs")
    date: date
    budget: int

    status: RecommendationStatus = Field(
        default=RecommendationStatus.PENDING,
        sa_column=Column(
            SAEnum(
                RecommendationStatus,
                native_enum=False,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=False,
        ),
    )

    plan_id: UUID | None = Field(default=None, foreign_key="plans.id")
