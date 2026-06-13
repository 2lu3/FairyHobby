from fastapi import Depends
from sqlmodel import Session, select
from uuid import UUID

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


def valid_user_id(user_id: UUID, session: Session = Depends(get_session)) -> UUID:
    """user_id が実在することを検証し、検証済みの UUID を返す。

    ルータ側は `user_id: UUID = Depends(valid_user_id)` として UUID を受け取り、
    各サービス（read/update/delete）に UUID として渡す。
    """
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError(f"User with id {user_id} not found")
    return user.id
