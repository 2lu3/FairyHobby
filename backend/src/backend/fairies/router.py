from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from sqlmodel import Session
from backend.database import get_db_session
from backend.users.dependencies import get_current_user
from backend.users.models import User
from backend.fairies.schemas import FairyReadResponse, FairyUpdateRequest
from backend.fairies.service import create, generate_embeddings, update
from backend.fairies.service import get_all, get
from uuid import UUID

router = APIRouter(
    prefix="/fairies",
    tags=["fairies"],
)


@router.post(
    "",
    response_model=FairyReadResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new fairy",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Conflict",
        },
    },
)
async def create_fairy(
    name: Annotated[str, Form()],
    prompt: Annotated[str, Form()],
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> FairyReadResponse:
    image_bytes = await image.read()
    image_content_type = image.content_type

    fairy = create(name, prompt, image_bytes, image_content_type, db_session)
    background_tasks.add_task(generate_embeddings, fairy.id)
    return FairyReadResponse.from_fairy(fairy)


@router.get(
    "",
    response_model=list[FairyReadResponse],
    description="List the fairies",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
    },
)
def get_fairies(
    db_session: Session = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[FairyReadResponse]:
    fairies = get_all(db_session)
    return [FairyReadResponse.from_fairy(fairy) for fairy in fairies]


@router.get(
    "/{fairy_id}",
    response_model=FairyReadResponse,
    description="Get a fairy",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def get_fairy(
    fairy_id: UUID,
    db_session: Session = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> FairyReadResponse:
    fairy = get(fairy_id, db_session)
    return FairyReadResponse.from_fairy(fairy)


@router.patch(
    "/{fairy_id}",
    response_model=FairyReadResponse,
    description="Update a fairy",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
        },
    },
)
def update_fairy(
    fairy_id: UUID,
    in_fairy: FairyUpdateRequest,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> FairyReadResponse:
    fairy = update(fairy_id, in_fairy, db_session)
    background_tasks.add_task(generate_embeddings, fairy.id)
    return FairyReadResponse.from_fairy(fairy)
