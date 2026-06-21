from uuid import UUID

from pydantic import BaseModel

from backend.activity_reviews.models import ActivityReview


class ActivityReviewCreateRequest(BaseModel):
    text: str
    activity_id: UUID


class ActivityReviewReadResponse(BaseModel):
    id: UUID
    text: str
    activity_id: UUID
    owner_user_id: UUID

    @classmethod
    def from_review(cls, review: ActivityReview) -> "ActivityReviewReadResponse":
        return cls(
            id=review.id,
            text=review.text,
            activity_id=review.activity_id,
            owner_user_id=review.owner_user_id,
        )


class ActivityReviewUpdateRequest(BaseModel):
    text: str | None
