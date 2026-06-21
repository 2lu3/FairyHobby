from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from backend.database import get_db_session
from backend.plans.schemas import PlanCreateRequest, PlanReadResponse, PlanUpdateRequest
from backend.plans.service import create, delete, get, update
from backend.users.dependencies import get_current_user
from backend.users.models import User

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
)


@router.post(
    "/",
    response_model=PlanReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new plan",
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
def create_plan(
    in_plan: PlanCreateRequest,
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> PlanReadResponse:
    plan = create(in_plan, db_session)
    return PlanReadResponse.from_plan(plan)


@router.get(
    "/{plan_id}",
    response_model=PlanReadResponse,
    description="Get a plan",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def get_plan(
    plan_id: UUID,
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> PlanReadResponse:
    plan = get(plan_id, db_session)
    return PlanReadResponse.from_plan(plan)


@router.patch(
    "/{plan_id}",
    response_model=PlanReadResponse,
    description="Update a plan",
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
def update_plan(
    plan_id: UUID,
    in_plan: PlanUpdateRequest,
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> PlanReadResponse:
    plan = update(plan_id, in_plan, db_session)
    return PlanReadResponse.from_plan(plan)


@router.delete(
    "/{plan_id}",
    response_model=PlanReadResponse,
    description="Delete a plan",
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
def delete_plan(
    plan_id: UUID,
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> PlanReadResponse:
    plan = get(plan_id, db_session)
    delete(plan_id, db_session)
    return PlanReadResponse.from_plan(plan)
