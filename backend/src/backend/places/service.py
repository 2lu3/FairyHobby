from backend.places.schemas import PlaceCreateRequest

from backend.places.models import Place
from sqlmodel import Session


def create(place: PlaceCreateRequest, session: Session) -> Place:
    session.add(place)
    session.commit()
    session.refresh(place)
    return place
