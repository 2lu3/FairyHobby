from sqlmodel import Field
from uuid import UUID
from backend.database import Base


class Activity(Base, table=True):
    __tablename__ = "activities"

    name: str
    description: str
    image_urls: list[str]

    place_id: UUID = Field(foreign_key="places.id")
