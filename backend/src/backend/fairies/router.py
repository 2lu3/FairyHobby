from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlmodel import Session
from backend.database import get_db_session
from backend.users.dependencies import get_current_user
from backend.users.models import User
from backend.fairies.schemas import FairyReadResponse
from backend.fairies.service import create

router = APIRouter(
    prefix="/fairies",
    tags=["fairies"],
)


@router.post(
    "/",
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
    _: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
) -> FairyReadResponse:
    image_bytes = await image.read()
    image_content_type = image.content_type

    fairy = create(name, prompt, image_bytes, image_content_type, db_session)
    return FairyReadResponse.from_fairy(fairy)
