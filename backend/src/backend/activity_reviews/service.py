import logging
from uuid import UUID

from sqlmodel import Session

from backend.activities.models import Activity
from backend.activity_reviews.models import ActivityReview
from backend.activity_reviews.schemas import (
    ActivityReviewCreateRequest,
    ActivityReviewUpdateRequest,
)
from backend.exceptions import NotFoundError, PermissionDeniedError
from backend.users.models import User

logger = logging.getLogger(__name__)


def create(
    in_review: ActivityReviewCreateRequest,
    current_user: User,
    db_session: Session,
) -> ActivityReview:
    activity = db_session.get(Activity, in_review.activity_id)
    if not activity:
        raise NotFoundError()

    review = ActivityReview(
        text=in_review.text,
        activity_id=in_review.activity_id,
        owner_user_id=current_user.id,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)
    logger.info("Created activity review %s by %s", review.id, current_user.id)

    return review


def get(review_id: UUID, db_session: Session) -> ActivityReview:
    review = db_session.get(ActivityReview, review_id)
    if not review:
        raise NotFoundError()
    return review


def update(
    review_id: UUID,
    in_review: ActivityReviewUpdateRequest,
    current_user: User,
    db_session: Session,
) -> ActivityReview:
    review = db_session.get(ActivityReview, review_id)
    if not review:
        raise NotFoundError()
    if review.owner_user_id != current_user.id:
        raise PermissionDeniedError()

    if in_review.text is not None:
        review.text = in_review.text

    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)
    logger.info("Updated activity review %s by %s", review.id, current_user.id)
    return review


def delete(
    review_id: UUID, current_user: User, db_session: Session
) -> tuple[ActivityReview, Activity]:
    review = db_session.get(ActivityReview, review_id)
    if not review:
        raise NotFoundError()
    if review.owner_user_id != current_user.id:
        raise PermissionDeniedError()

    activity = db_session.get(Activity, review.activity_id)
    if not activity:
        raise NotFoundError()

    db_session.delete(review)
    db_session.commit()
    db_session.refresh(activity)
    logger.info("Deleted activity review %s by %s", review_id, current_user.id)
    return review, activity
