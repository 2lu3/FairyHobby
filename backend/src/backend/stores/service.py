import logging
from uuid import UUID

from sqlmodel import Session

from backend.exceptions import NotFoundError, PermissionDeniedError
from backend.stores.models import Store
from backend.stores.schemas import StoreCreateRequest, StoreUpdateRequest
from backend.users.models import User

logger = logging.getLogger(__name__)


def create(
    in_store: StoreCreateRequest, current_user: User, db_session: Session
) -> Store:
    store = Store(
        name=in_store.name,
        description=in_store.description,
        owner_user_id=current_user.id,
    )
    db_session.add(store)
    db_session.commit()
    db_session.refresh(store)
    logger.info("Created store %s by %s", store.id, current_user.id)
    return store


def get(store_id: UUID, db_session: Session) -> Store:
    store = db_session.get(Store, store_id)
    if not store:
        raise NotFoundError()
    return store


def update(
    store_id: UUID,
    in_store: StoreUpdateRequest,
    current_user: User,
    db_session: Session,
) -> Store:
    store = db_session.get(Store, store_id)
    if not store:
        raise NotFoundError()
    if store.owner_user_id != current_user.id:
        raise PermissionDeniedError()
    store.name = in_store.name
    store.description = in_store.description
    db_session.add(store)
    db_session.commit()
    db_session.refresh(store)
    logger.info("Updated store %s by %s", store.id, current_user.id)
    return store


def delete(store_id: UUID, current_user: User, db_session: Session) -> Store:
    store = db_session.get(Store, store_id)
    if not store:
        raise NotFoundError()
    if store.owner_user_id != current_user.id:
        raise PermissionDeniedError()
    db_session.delete(store)
    db_session.commit()
    logger.info("Deleted store %s by %s", store_id, current_user.id)
    return store
