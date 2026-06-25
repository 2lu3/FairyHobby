from sqlmodel import Field
from backend.database import Base
from sqlmodel import Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.activities.models import Activity
    from backend.activity_reviews.models import ActivityReview


class User(Base, table=True):
    __tablename__ = "users"

    firebase_uid: str = Field(unique=True)
    email: str = Field(unique=True)
    display_name: str
    icon: str
    is_admin: bool

    activities: list["Activity"] = Relationship(back_populates="owner_user")
    activity_reviews: list["ActivityReview"] = Relationship(back_populates="owner_user")
