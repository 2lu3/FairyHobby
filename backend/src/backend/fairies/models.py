from backend.database import Base
from sqlmodel import Field


class Fairy(Base, table=True):
    __tablename__ = "fairies"

    name: str = Field(unique=True)
    prompt: str
    image_path: str
    image_content_type: str
