from fastapi import Depends
from sqlmodel import Session

from backend.auth.dependencies import get_session_user_id
from backend.database import get_db_session
from uuid import UUID
from .models import User
from .service import get


def get_current_user(
    user_id: UUID = Depends(get_session_user_id),
    db_session: Session = Depends(get_db_session),
) -> User:
    return get(user_id, db_session)
