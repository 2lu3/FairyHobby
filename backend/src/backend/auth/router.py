from fastapi import APIRouter, Depends, Request, status
from sqlmodel import Session
from backend.auth.dependencies import get_firebase_uid
from backend.database import get_db_session
from backend.users.service import get_by_firebase_uid
from .schemas import CreateSessionResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/session",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_200_OK,
    description="Create a new session",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
        },
    },
)
def create_session(
    request: Request,
    firebase_uid: str = Depends(get_firebase_uid),
    session: Session = Depends(get_db_session),
):
    user = get_by_firebase_uid(firebase_uid, session)

    if user:
        request.session["user_id"] = str(user.id)
        return CreateSessionResponse(id=user.id, needs_signup=False)

    return CreateSessionResponse(id=None, needs_signup=True)


@router.delete(
    "/session",
    status_code=status.HTTP_200_OK,
    description="Logout the user",
)
def delete_session(
    request: Request,
):
    request.session.clear()
    return
