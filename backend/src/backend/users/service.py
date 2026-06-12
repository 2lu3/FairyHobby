from uuid import UUID

from sqlmodel import Session, select

from backend.auth.service import get_email_from_firebase
from backend.users.models import User
from backend.users.schemas import (
    UserCreateRequest,
    UserDeleteResponse,
    UserReadResponse,
    UserUpdateRequest,
    UserMeReadResponse,
)
from backend.users.exceptions import (
    UserAlreadyExistsError,
    PermissionDeniedError,
    UserNotFoundError,
)


def create_user(
    in_user: UserCreateRequest, firebase_uid: str, session: Session
) -> UserMeReadResponse:
    existing_user = session.exec(
        select(User).where(User.firebase_uid == firebase_uid)
    ).first()
    if existing_user:
        raise UserAlreadyExistsError(
            f"User with firebase uid {firebase_uid} already exists"
        )

    user = User(
        firebase_uid=firebase_uid,
        email=get_email_from_firebase(firebase_uid),
        display_name=in_user.display_name,
        is_admin=False,
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def read_user(user_id: UUID, session: Session) -> UserReadResponse:
    """ログイン済みユーザーが、任意のユーザーの公開情報を取得する"""
    # 対象ユーザーが存在するか確認する
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError(f"User with id {user_id} not found")

    return user


def update_user(
    user_id: UUID, in_user: UserUpdateRequest, current_user: User, session: Session
) -> UserReadResponse:
    """自身もしくは他のユーザーの情報を更新する
    Raises:
        UserNotFoundError: 対象ユーザーが存在しない
        PermissionDeniedError: 非管理者が他のユーザーの情報を更新しようとした
    """

    if user_id == current_user.id:
        target_user = current_user
    else:
        target_user = session.get(User, user_id)
        if not target_user:
            raise UserNotFoundError(f"User with id {user_id} not found")

    if in_user.display_name is not None:
        target_user.display_name = in_user.display_name

    if in_user.is_admin is not None:
        if current_user.is_admin:
            target_user.is_admin = in_user.is_admin
        else:
            raise PermissionDeniedError("You are not admin")

    session.add(target_user)
    session.commit()
    session.refresh(target_user)
    return target_user


def delete_user(user_id: UUID, current_user, session: Session) -> UserDeleteResponse:
    if user_id == current_user.id:
        target_user = current_user
    else:
        target_user = session.get(User, user_id)
        if not target_user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if not current_user.is_admin:
            raise PermissionDeniedError("Only admin can delete other users")

    session.delete(target_user)
    session.commit()

    return UserDeleteResponse(id=target_user.id)
