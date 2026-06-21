from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from backend.database import Base

if TYPE_CHECKING:
    from backend.activities.models import Activity
    from backend.users.models import User


class ActivityReview(Base, table=True):
    __tablename__ = "activity_reviews"

    text: str

    activity_id: UUID = Field(foreign_key="activities.id")
    activity: "Activity" = Relationship(back_populates="reviews")

    owner_user_id: UUID = Field(foreign_key="users.id")
    owner_user: "User" = Relationship(back_populates="activity_reviews")
