from pydantic import BaseModel
from uuid import UUID
from backend.fairies.models import Fairy
from backend.storage import get_presigned_url


class FairyCreateRequest(BaseModel):
    name: str
    prompt: str


class FairyReadResponse(BaseModel):
    id: UUID
    name: str
    prompt: str
    image_url: str

    @classmethod
    def from_fairy(cls, fairy: Fairy) -> "FairyReadResponse":
        return cls(
            id=fairy.id,
            name=fairy.name,
            prompt=fairy.prompt,
            image_url=get_presigned_url(fairy.image_path),
        )


class FairyUpdateRequest(BaseModel):
    name: str | None
    prompt: str | None
