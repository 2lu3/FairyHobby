from fastapi import Depends
from sqlmodel import Session, select

from backend.auth.dependencies import get_firebase_uid
from backend.database import get_session
from backend.users.models import User
from backend.users.exceptions import UserNotFoundError


def get_current_user(
    firebase_uid: str = Depends(get_firebase_uid),
    session: Session = Depends(get_session),
) -> User:
    """ログイン済みユーザーを取得する
    Raises:
        UserNotFoundError:
        TokenVerificationError:
    """
    user = session.exec(select(User).where(User.firebase_uid == firebase_uid)).first()
    if not user:
        raise UserNotFoundError(f"User with firebase uid {firebase_uid} not found")
    return user