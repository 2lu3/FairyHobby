from pydantic import BaseModel
from uuid import UUID


class StoreCreateRequest(BaseModel):
    name: str
    description: str


class StoreReadResponse(BaseModel):
    id: UUID
    name: str
    description: str
    owner_id: UUID


class StoreUpdateRequest(BaseModel):
    name: str | None
    description: str | None
