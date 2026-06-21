from fastapi import APIRouter, status, Depends, BackgroundTasks
from sqlmodel import Session
from uuid import UUID
from backend.database import get_db_session
from backend.users.dependencies import get_current_user
from backend.users.models import User
from .schemas import ActivityReadResponse, ActivityCreateRequest, ActivityUpdateRequest
from .service import create, get, update, delete, generate_preference_and_embeddings

router = APIRouter(
    prefix="/activities",
    tags=["activities"],
)


@router.post(
    "/",
    response_model=ActivityReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new activity",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def create_activity(
    activity: ActivityCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> ActivityReadResponse:
    activity = create(activity, current_user, db_session)
    background_tasks.add_task(generate_preference_and_embeddings, activity.id)
    return ActivityReadResponse.from_activity(activity)


@router.get(
    "/{activity_id}",
    response_model=ActivityReadResponse,
    description="Get an activity",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def get_activity(
    activity_id: UUID,
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> ActivityReadResponse:
    activity = get(activity_id, db_session)
    return ActivityReadResponse.from_activity(activity)


@router.patch(
    "/{activity_id}",
    response_model=ActivityReadResponse,
    description="Update an activity",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def update_activity(
    activity_id: UUID,
    in_activity: ActivityUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> ActivityReadResponse:
    activity = update(activity_id, in_activity, current_user, db_session)
    background_tasks.add_task(generate_preference_and_embeddings, activity.id)
    return ActivityReadResponse.from_activity(activity)


@router.delete(
    "/{activity_id}",
    response_model=ActivityReadResponse,
    description="Delete an activity",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def delete_activity(
    activity_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    activity = delete(activity_id, current_user, db_session)
    return ActivityReadResponse.from_activity(activity)
