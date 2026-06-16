from fastapi import APIRouter
from fastapi import status
from sqlmodel import Session, Depends
from uuid import UUID
from backend.database import get_db_session
from .schemas import ActivityReadResponse, ActivityCreateRequest

activities_router = APIRouter(
    prefix="/activities",
    tags=["activities"],
)


@activities_router.post(
    "/",
    response_model=ActivityReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new activity",
)
def create_activity(
    activity: ActivityCreateRequest, session: Session = Depends(get_db_session)
) -> ActivityReadResponse:
    return {}


@activities_router.get(
    "/{activity_id}",
    response_model=ActivityReadResponse,
    description="Read an activity",
)
def read_activity(
    activity_id: UUID,
    session: Session = Depends(get_db_session),
) -> ActivityReadResponse:
    return {}
