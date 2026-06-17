from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from backend.database import get_db_session
from backend.stores.schemas import (
    StoreCreateRequest,
    StoreReadResponse,
    StoreUpdateRequest,
)
from backend.users.dependencies import get_current_user
from backend.users.models import User
from backend.stores.service import create, get, update, delete
from uuid import UUID

router = APIRouter(
    prefix="/stores",
    tags=["stores"],
)


@router.post(
    "/",
    response_model=StoreReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new store",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
    },
)
def create_store(
    store: StoreCreateRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> StoreReadResponse:
    return create(store, current_user, db_session)


@router.get(
    "/{store_id}",
    response_model=StoreReadResponse,
    description="Get a store",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def get_store(
    store_id: UUID,
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> StoreReadResponse:
    return get(store_id, db_session)


@router.patch(
    "/{store_id}",
    response_model=StoreReadResponse,
    description="Update a store",
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
def update_store(
    store_id: UUID,
    in_store: StoreUpdateRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> StoreReadResponse:
    return update(store_id, in_store, current_user, db_session)


@router.delete(
    "/{store_id}",
    response_model=StoreReadResponse,
    description="Delete a store",
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
def delete_store(
    store_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> StoreReadResponse:
    return delete(store_id, current_user, db_session)
