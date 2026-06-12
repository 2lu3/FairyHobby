from sqlmodel import Field
from pydantic import EmailStr
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    firebase_uid: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    display_name: str
    is_admin: bool = False