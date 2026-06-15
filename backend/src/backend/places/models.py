from backend.database import Base
from sqlmodel import CheckConstraint


class Place(Base, table=True):
    __tablename__ = "places"
    __table_args__ = [
        CheckConstraint(
            "(latitude IS NOT NULL AND longitude IS NOT NULL) OR (latitude IS NULL AND longitude IS NULL)",
            name="check_latitude_and_longitude",
        )
    ]

    name: str

    address: str | None
    latitude: float | None
    longitude: float | None
