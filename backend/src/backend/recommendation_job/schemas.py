from datetime import date
from uuid import UUID

from pydantic import BaseModel

from .models import RecommendationJob, RecommendationStatus


class RecommendationJobCreateRequest(BaseModel):
    fairy_id: UUID
    latitude: float
    longitude: float
    date: date
    budget: int


class RecommendationJobReadResponse(BaseModel):
    id: UUID
    status: RecommendationStatus
    plan_id: UUID | None

    @classmethod
    def from_recommendation_job(
        cls, recommendation_job: RecommendationJob
    ) -> "RecommendationJobReadResponse":
        return cls(
            id=recommendation_job.id,
            status=recommendation_job.status,
            plan_id=recommendation_job.plan_id,
        )


class RecommendationJobStatusResponse(BaseModel):
    status: RecommendationStatus
    plan_id: UUID | None

    @classmethod
    def from_recommendation_job(
        cls, recommendation_job: RecommendationJob
    ) -> "RecommendationJobStatusResponse":
        return cls(
            status=recommendation_job.status,
            plan_id=recommendation_job.plan_id,
        )
