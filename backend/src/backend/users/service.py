from uuid import UUID

from sqlmodel import Session, select

from backend.auth.service import get_email_from_firebase
from backend.users.models import User
from backend.users.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
)
from backend.exceptions import NotFoundError, ConflictError, PermissionDeniedError


def create(in_user: UserCreateRequest, firebase_uid: str, session: Session) -> User:
    existing_user = session.exec(
        select(User).where(User.firebase_uid == firebase_uid)
    ).first()
    if existing_user:
        raise ConflictError()

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


def get(user_id: UUID, session: Session) -> User:
    user = session.get(User, user_id)
    if not user:
        raise NotFoundError()

    return user


def get_all(session: Session) -> list[User]:
    users = session.exec(select(User)).all()
    return users


def update(
    user_id: UUID, in_user: UserUpdateRequest, current_user: User, session: Session
) -> User:
    """自身もしくは他のユーザーの情報を更新する
    Raises:
        NotFoundError: 対象ユーザーが存在しない
        PermissionDeniedError: 非管理者が他のユーザーの情報を更新しようとした
    """

    target_user = (
        current_user if user_id == current_user.id else session.get(User, user_id)
    )

    if not target_user:
        raise NotFoundError()
    if current_user.id != target_user.id and not current_user.is_admin:
        raise PermissionDeniedError()

    if in_user.display_name is not None:
        target_user.display_name = in_user.display_name

    if in_user.is_admin is not None:
        if current_user.is_admin:
            target_user.is_admin = in_user.is_admin
        else:
            raise PermissionDeniedError()

    session.add(target_user)
    session.commit()
    session.refresh(target_user)
    return target_user


def delete(user_id: UUID, current_user: User, session: Session) -> User:
    if user_id == current_user.id:
        target_user = current_user
    else:
        target_user = session.get(User, user_id)
        if not target_user:
            raise NotFoundError()
        if not current_user.is_admin:
            raise PermissionDeniedError()

    session.delete(target_user)
    session.commit()
    return target_user
