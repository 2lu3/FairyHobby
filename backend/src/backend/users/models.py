from sqlmodel import Field
from backend.database import Base


class User(Base, table=True):
    __tablename__ = "users"

    firebase_uid: str = Field(unique=True)
    email: str = Field(unique=True)
    display_name: str
    is_admin: bool
