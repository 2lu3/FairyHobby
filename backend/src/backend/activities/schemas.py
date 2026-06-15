from pydantic import BaseModel
from uuid import UUID


class ActivityCreateRequest(BaseModel):
    name: str
    description: str
    image_urls: list[str]

    address: str | None
    latitude: float | None
    longitude: float | None


class ActivityReadResponse(BaseModel):
    id: UUID
    name: str
    description: str

    address: str | None
    latitude: float | None
    longitude: float | None


class ActivityUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    image_urls: list[str]
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
