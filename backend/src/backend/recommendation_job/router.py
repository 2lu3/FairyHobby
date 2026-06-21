from fastapi import APIRouter, BackgroundTasks

from backend.recommendation_job.schemas import (
    RecommendationJobCreateRequest,
    RecommendationJobStatus,
    RecommendationJobReadResponse,
)
from backend.users.dependencies import get_current_user
from backend.users.models import User
from backend.database import get_db_session
from sqlmodel import Session
from fastapi import status, Depends
from uuid import UUID
from backend.recommendation_job.service import get_status, generate_recommendation


router = APIRouter(
    prefix="/recommendation",
    tags=["recommendation"],
)


@router.post(
    "/jobs",
    response_model=RecommendationJobStatus,
    status_code=status.HTTP_201_CREATED,
    description="Create a new recommendation job",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
    },
)
def create_recommendation_job(
    recommendation_job: RecommendationJobCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> RecommendationJobReadResponse:
    recommendation_job = create_recommendation_job(
        recommendation_job, current_user, db_session
    )

    background_tasks.add_task(
        generate_recommendation, recommendation_job.id, db_session
    )
    return RecommendationJobReadResponse.from_recommendation_job(recommendation_job)


@router.get(
    "/jobs/{job_id}/status",
    response_model=RecommendationJobStatus,
    status_code=status.HTTP_200_OK,
    description="Get the status of a recommendation job",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def get_recommendation_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> RecommendationJobStatus:
    status = get_status(job_id, current_user, db_session)
    return RecommendationJobStatus(status=status)
