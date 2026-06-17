from pydantic import BaseModel
from uuid import UUID
from backend.activities.models import Activity


class ActivityCreateRequest(BaseModel):
    name: str
    description: str
    price: int
    image_urls: list[str]

    owner_store_id: UUID

    address: str | None
    latitude: float | None
    longitude: float | None


class ActivityReadResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: int
    image_urls: list[str]

    owner_store_id: UUID

    address: str | None
    latitude: float | None
    longitude: float | None

    @classmethod
    def from_activity(cls, activity: Activity) -> "ActivityReadResponse":
        return cls(
            id=activity.id,
            name=activity.name,
            description=activity.description,
            price=activity.price,
            image_urls=[image.image_url for image in activity.images],
            owner_store_id=activity.owner_store_id,
            address=activity.address,
            latitude=activity.latitude,
            longitude=activity.longitude,
        )


class ActivityUpdateRequest(BaseModel):
    name: str | None
    description: str | None
    price: int | None
    image_urls: list[str] | None

    address: str | None
    latitude: float | None
    longitude: float | None
