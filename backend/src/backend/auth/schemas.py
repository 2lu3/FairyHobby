from pydantic import BaseModel
from uuid import UUID


class CreateSessionResponse(BaseModel):
    id: UUID | None
    needs_signup: bool
