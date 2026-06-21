import datetime
from pydantic import BaseModel
from uuid import UUID
from .models import RecommendationStatus, RecommendationJob


class RecommendationJobCreateRequest(BaseModel):
    fairy_id: UUID
    latitude: float
    longitude: float
    start_date: datetime
    end_date: datetime
    budget: int


class RecommendationJobReadResponse(BaseModel):
    id: UUID
    status: RecommendationStatus

    @classmethod
    def from_recommendation_job(
        cls, recommendation_job: RecommendationJob
    ) -> "RecommendationJobReadResponse":
        return cls(
            id=recommendation_job.id,
            status=recommendation_job.status,
        )
