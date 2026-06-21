from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from backend.database import get_db_session
from backend.plan_histories.schemas import (
    PlanHistoryCreateRequest,
    PlanHistoryDeleteResponse,
    PlanHistoryReadResponse,
    PlanHistoryUpdateRequest,
)
from backend.plan_histories.service import (
    create,
    delete,
    get,
    get_all,
    update,
)
from backend.users.dependencies import get_current_user
from backend.users.models import User

router = APIRouter(
    prefix="/plan-histories",
    tags=["plan_histories"],
)


@router.post(
    "",
    response_model=PlanHistoryReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new plan history",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def create_plan_history(
    in_plan_history: PlanHistoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    return create(in_plan_history, current_user, db_session)


@router.get(
    "",
    response_model=list[PlanHistoryReadResponse],
    description="List the current user's plan histories",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
    },
)
def get_plan_histories(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    return get_all(current_user, db_session)


@router.get(
    "/{plan_history_id}",
    response_model=PlanHistoryReadResponse,
    description="Get a plan history",
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
def get_plan_history(
    plan_history_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    return get(plan_history_id, current_user, db_session)


@router.patch(
    "/{plan_history_id}",
    response_model=PlanHistoryReadResponse,
    description="Update a plan history",
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
def update_plan_history(
    plan_history_id: UUID,
    in_plan_history: PlanHistoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    return update(plan_history_id, in_plan_history, current_user, db_session)


@router.delete(
    "/{plan_history_id}",
    response_model=PlanHistoryDeleteResponse,
    description="Delete a plan history",
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
def delete_plan_history(
    plan_history_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    return delete(plan_history_id, current_user, db_session)
