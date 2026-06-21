from uuid import UUID

from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlmodel import Session

from backend.activity_reviews.schemas import (
    ActivityReviewCreateRequest,
    ActivityReviewReadResponse,
    ActivityReviewUpdateRequest,
)
from backend.activity_reviews.service import create, delete, get, update
from backend.database import get_db_session
from backend.users.dependencies import get_current_user
from backend.users.models import User
from backend.activities.service import generate_preference_and_embeddings

router = APIRouter(
    prefix="/activity-reviews",
    tags=["activity-reviews"],
)


@router.post(
    "/",
    response_model=ActivityReviewReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new activity review",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def create_activity_review(
    review: ActivityReviewCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> ActivityReviewReadResponse:
    review = create(review, current_user, db_session)
    background_tasks.add_task(generate_preference_and_embeddings, review.activity_id)
    return ActivityReviewReadResponse.from_review(review)


@router.get(
    "/{review_id}",
    response_model=ActivityReviewReadResponse,
    description="Get an activity review",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def get_activity_review(
    review_id: UUID,
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> ActivityReviewReadResponse:
    review = get(review_id, db_session)
    return ActivityReviewReadResponse.from_review(review)


@router.patch(
    "/{review_id}",
    response_model=ActivityReviewReadResponse,
    description="Update an activity review",
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
def update_activity_review(
    review_id: UUID,
    in_review: ActivityReviewUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> ActivityReviewReadResponse:
    review = update(review_id, in_review, current_user, db_session)
    background_tasks.add_task(generate_preference_and_embeddings, review.activity_id)
    return ActivityReviewReadResponse.from_review(review)


@router.delete(
    "/{review_id}",
    response_model=ActivityReviewReadResponse,
    description="Delete an activity review",
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
def delete_activity_review(
    review_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> ActivityReviewReadResponse:
    review, activity = delete(review_id, current_user, db_session)
    background_tasks.add_task(generate_preference_and_embeddings, activity.id)
    return ActivityReviewReadResponse.from_review(review)
