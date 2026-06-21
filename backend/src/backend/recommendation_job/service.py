from uuid import UUID

from sqlmodel import Session

from backend.activities.models import Activity
from backend.exceptions import NotFoundError, PermissionDeniedError
from backend.plans.models import Plan, PlanItem
from backend.recommendation_job.models import RecommendationJob, RecommendationStatus
from backend.recommendation_job.schemas import RecommendationJobCreateRequest
from backend.recommendation_job.worker import Optimizer
from backend.users.models import User


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
        date=in_recommendation_job.date,
        budget=in_recommendation_job.budget,
    )
    db_session.add(recommendation_job)
    db_session.commit()
    db_session.refresh(recommendation_job)

    return recommendation_job


def get_job_for_user(
    job_id: UUID, current_user: User, db_session: Session
) -> RecommendationJob:
    recommendation_job = db_session.get(RecommendationJob, job_id)
    if not recommendation_job:
        raise NotFoundError()
    if current_user.id != recommendation_job.user_id:
        raise PermissionDeniedError()
    return recommendation_job


def get_job(job_id: UUID, db_session: Session) -> RecommendationJob:
    recommendation_job = db_session.get(RecommendationJob, job_id)
    if not recommendation_job:
        raise NotFoundError()
    return recommendation_job


def _create_plan_from_result(
    activities: list[Activity],
    db_session: Session,
) -> UUID:
    plan = Plan(
        name="妖精が選んだプラン",
        description="妖精が選んだプランです",
    )
    for position, activity in enumerate(activities):
        plan.items.append(
            PlanItem(
                position=position,
                activity_id=activity.id,
            )
        )
    db_session.add(plan)
    db_session.flush()
    return plan.id


def generate_recommendation(job_id: UUID, db_session: Session) -> None:
    recommendation_job = get_job(job_id, db_session)
    if recommendation_job.status != RecommendationStatus.PENDING:
        return

    recommendation_job.status = RecommendationStatus.CALCULATING
    db_session.commit()
    db_session.refresh(recommendation_job)

    try:
        optimizer = Optimizer(recommendation_job, db_session)
        optimizer.build_model()
        activities = optimizer.run()
        if activities:
            recommendation_job.plan_id = _create_plan_from_result(
                activities, db_session
            )
    except Exception:
        recommendation_job.status = RecommendationStatus.FAILED
        db_session.commit()
        db_session.refresh(recommendation_job)
        raise

    recommendation_job.status = RecommendationStatus.COMPLETED
    db_session.commit()
    db_session.refresh(recommendation_job)
