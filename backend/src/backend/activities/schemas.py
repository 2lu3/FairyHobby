from uuid import UUID

from pydantic import BaseModel

from backend.activities.models import Activity
from backend.activity_reviews.schemas import ActivityReviewReadResponse


class ActivityCreateRequest(BaseModel):
    name: str
    description: str
    price: int
    duration_minutes: int
    image_urls: list[str]

    address: str | None


class ActivityReadResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: int
    duration_minutes: int
    image_urls: list[str]

    owner_user_id: UUID

    address: str | None

    reviews: list[ActivityReviewReadResponse]

    @classmethod
    def from_activity(cls, activity: Activity) -> "ActivityReadResponse":
        return cls(
            id=activity.id,
            name=activity.name,
            description=activity.description,
            price=activity.price,
            duration_minutes=activity.duration_minutes,
            image_urls=[image.image_url for image in activity.images],
            owner_user_id=activity.owner_user_id,
            address=activity.address,
            reviews=[
                ActivityReviewReadResponse.from_review(review)
                for review in activity.reviews
            ],
        )


class ActivityUpdateRequest(BaseModel):
    name: str | None
    description: str | None
    price: int | None
    duration_minutes: int | None
    image_urls: list[str] | None

    address: str | None

    preference_text: str | None
