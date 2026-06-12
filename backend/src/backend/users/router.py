from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from uuid import UUID

from backend.auth.dependencies import get_firebase_uid
from backend.database import get_session
from backend.users.schemas import (
    UserCreateRequest,
    UserMeReadResponse,
    UserReadResponse,
    UserUpdateRequest,
    UserDeleteResponse,
)
from backend.users.service import (
    create_user as create_user_service,
    # asで別名にしなくても衝突しないが、service由来である他の関数と合わせた方が読みやすいため
    read_user as read_user_service,
    update_user as update_user_service,
    delete_user as delete_user_service,
)
from backend.users.dependencies import get_current_user, valid_user_id
from backend.users.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/",
    response_model=UserReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new user",
    summary="Create a new user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Conflict",
        },
    },
)
def create_user(
    in_user: UserCreateRequest,
    firebase_uid: str = Depends(get_firebase_uid),
    session: Session = Depends(get_session),
):
    user = create_user_service(in_user, firebase_uid, session)
    return user


@router.get(
    "/me",
    response_model=UserMeReadResponse,
    description="Read the current user's information",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def get_user_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserReadResponse,
    description="Read the user's information",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def get_user(
    user_id: UUID = Depends(valid_user_id),
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    user = read_user_service(user_id, session)
    return user


@router.patch(
    "/{user_id}",
    response_model=UserReadResponse,
    description="Update the user's information",
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
def update_user(
    in_user: UserUpdateRequest,
    user_id: UUID = Depends(valid_user_id),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = update_user_service(user_id, in_user, current_user, session)
    return user


@router.delete(
    "/{user_id}",
    response_model=UserDeleteResponse,
    description="Delete the user's information",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def delete_user(
    user_id: UUID = Depends(valid_user_id),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return delete_user_service(user_id, current_user, session)
