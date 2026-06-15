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
    create,
    get,
    update,
    delete,
    get_all,
)
from backend.users.dependencies import get_current_user
from backend.users.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    response_model=UserReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new user",
    summary="Create a new user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
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
    user = create(in_user, firebase_uid, session)
    return user


@router.get(
    "",
    response_model=list[UserReadResponse],
    description="List the users' information",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
    },
)
def get_users(
    session: Session = Depends(get_session),
    # _: User = Depends(get_current_user), TODO: 後であんコメントする
):
    users = get_all(session)
    return users


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
    user_id: UUID,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    user = get(user_id, session)
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
    user_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user = update(user_id, in_user, current_user, session)
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
    user_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return delete(user_id, current_user, session)
