from backend.activities.schemas import ActivityCreateRequest, ActivityUpdateRequest
from backend.activities.models import Activity
from sqlmodel import Session
from uuid import UUID


def create(activity: ActivityCreateRequest, session: Session) -> Activity:

    pass


def get(activity_id: UUID, session: Session) -> Activity:
    pass


def update(
    activity_id: UUID, activity: ActivityUpdateRequest, session: Session
) -> Activity:
    pass


def delete(activity_id: UUID, session: Session) -> Activity:
    pass
