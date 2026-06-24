from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship

from backend.database import Base
from backend.users.models import User

if TYPE_CHECKING:
    from backend.activity_reviews.models import ActivityReview


class Activity(Base, table=True):
    __tablename__ = "activities"

    name: str
    description: str
    price: int
    duration_minutes: int
    images: list["ActivityImage"] = Relationship(
        back_populates="activity",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    owner_user_id: UUID = Field(foreign_key="users.id")
    owner_user: "User" = Relationship(back_populates="activities")

    address: str | None

    preference_text: str | None = None

    reviews: list["ActivityReview"] = Relationship(
        back_populates="activity",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    embeddings: list[float] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )


class ActivityImage(Base, table=True):
    __tablename__ = "activity_images"

    image_url: str

    activity_id: UUID = Field(foreign_key="activities.id")
    activity: "Activity" = Relationship(back_populates="images")
