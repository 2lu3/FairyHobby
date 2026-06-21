from backend.recommendation.schemas import RecommendationJobCreateRequest
from backend.recommendation.models import RecommendationJob, RecommendationStatus
from backend.users.models import User
from sqlmodel import Session
from uuid import UUID
from backend.exceptions import NotFoundError, PermissionDeniedError


def create_job(
    in_recommendation_job: RecommendationJobCreateRequest,
    current_user: User,
    db_session: Session,
) -> RecommendationJob:
    recommendation_job = RecommendationJob(
        fairy_id=in_recommendation_job.fairy_id,
        user_id=current_user.id,
        latitude=in_recommendation_job.latitude,
        longitude=in_recommendation_job.longitude,
        start_date=in_recommendation_job.start_date,
        end_date=in_recommendation_job.end_date,
        budget=in_recommendation_job.budget,
    )
    db_session.add(recommendation_job)
    db_session.commit()
    db_session.refresh(recommendation_job)

    return recommendation_job


def get_status(
    job_id: UUID, current_user: User, db_session: Session
) -> RecommendationStatus:

    recommendation_job = db_session.get(RecommendationJob, job_id)
    if not recommendation_job:
        raise NotFoundError()
    if current_user.id != recommendation_job.user_id:
        raise PermissionDeniedError()
    return recommendation_job.status


def get_job(job_id: UUID, db_session: Session) -> RecommendationJob:
    recommendation_job = db_session.get(RecommendationJob, job_id)
    if not recommendation_job:
        raise NotFoundError()
    return recommendation_job


def generate_recommendation(job_id: UUID, db_session: Session):
    recommendation_job = get_job(job_id, db_session)
    if recommendation_job.status != RecommendationStatus.PENDING:
        return

    recommendation_job.status = RecommendationStatus.CALCULATING
    db_session.commit()
    db_session.refresh(recommendation_job)

    try:
        pass

    except Exception as e:
        recommendation_job.status = RecommendationStatus.FAILED
        db_session.commit()
        db_session.refresh(recommendation_job)
        raise e

    recommendation_job.status = RecommendationStatus.COMPLETED
    db_session.commit()
    db_session.refresh(recommendation_job)
