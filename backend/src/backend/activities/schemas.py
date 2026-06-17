from pydantic import BaseModel
from uuid import UUID


class ActivityCreateRequest(BaseModel):
    name: str
    description: str
    image_urls: list[str]

    owner_store_id: UUID

    address: str | None
    latitude: float | None
    longitude: float | None


class ActivityReadResponse(BaseModel):
    id: UUID
    name: str
    description: str
    image_urls: list[str]

    onwer_store_id: UUID

    address: str | None
    latitude: float | None
    longitude: float | None


class ActivityUpdateRequest(BaseModel):
    name: str | None
    description: str | None
    image_urls: list[str] | None

    address: str | None
    latitude: float | None
    longitude: float | None
