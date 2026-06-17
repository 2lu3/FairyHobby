from backend.database import Base
from sqlmodel import Field
from uuid import UUID
from sqlmodel import Relationship
from backend.stores.models import Store
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.stores.models import Store


class Activity(Base, table=True):
    __tablename__ = "activities"

    name: str
    description: str
    image_urls: list[str]

    owner_store_id: UUID = Field(foreign_key="stores.id")
    owner_store: "Store" = Relationship(back_populates="activities")

    address: str | None
    latitude: float | None
    longitude: float | None
