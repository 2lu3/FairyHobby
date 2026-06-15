from pydantic import BaseModel
from uuid import UUID


class PlaceCreateRequest(BaseModel):
    name: str
    description: str
    image_url: str

    address: str | None
    latitude: float | None
    longitude: float | None


class PlaceReadResponse(BaseModel):
    id: UUID
    name: str
    description: str
    image_url: str

    address: str | None
    latitude: float | None
    longitude: float | None


class PlaceUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    image_url: str | None = None

    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
