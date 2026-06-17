from backend.database import Base
from sqlmodel import Field
from uuid import UUID
from typing import TYPE_CHECKING
from sqlmodel import Relationship

if TYPE_CHECKING:
    from backend.users.models import User
    from backend.activities.models import Activity


class Store(Base, table=True):
    __tablename__ = "stores"

    name: str
    description: str

    owner_user_id: UUID = Field(foreign_key="users.id")
    owner_user: "User" = Relationship(back_populates="stores")

    activities: list["Activity"] = Relationship(back_populates="owner_store")
