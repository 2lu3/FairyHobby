from backend.activities.schemas import ActivityCreateRequest, ActivityUpdateRequest
from backend.activities.models import Activity, ActivityImage
from backend.users.models import User
from sqlmodel import Session
from uuid import UUID
from backend.exceptions import NotFoundError, PermissionDeniedError
from backend.stores.models import Store


def create(
    in_activity: ActivityCreateRequest, current_user: User, db_session: Session
) -> Activity:
    # ログイン中のユーザーがstoreの所有者であるか確認する
    store = db_session.get(Store, in_activity.owner_store_id)
    if not store:
        raise NotFoundError()
    if store.owner_user_id != current_user.id:
        raise PermissionDeniedError()

    activity = Activity(
        name=in_activity.name,
        description=in_activity.description,
        price=in_activity.price,
        owner_store_id=in_activity.owner_store_id,
        address=in_activity.address,
        latitude=in_activity.latitude,
        longitude=in_activity.longitude,
    )

    for image_url in in_activity.image_urls:
        activity_image = ActivityImage(image_url=image_url)
        activity.images.append(activity_image)

    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    return activity


def get(activity_id: UUID, db_session: Session) -> Activity:
    activity = db_session.get(Activity, activity_id)
    if not activity:
        raise NotFoundError()
    return activity


def update(
    activity_id: UUID,
    in_activity: ActivityUpdateRequest,
    current_user: User,
    db_session: Session,
) -> Activity:
    activity = db_session.get(Activity, activity_id)
    if not activity:
        raise NotFoundError()

    store = db_session.get(Store, activity.owner_store_id)
    if not store:
        raise NotFoundError()
    if store.owner_user_id != current_user.id:
        raise PermissionDeniedError()

    if in_activity.name is not None:
        activity.name = in_activity.name
    if in_activity.description is not None:
        activity.description = in_activity.description
    if in_activity.price is not None:
        activity.price = in_activity.price
    if in_activity.image_urls is not None:
        activity.image_urls = in_activity.image_urls
    if in_activity.address is not None:
        activity.address = in_activity.address
    if in_activity.latitude is not None:
        activity.latitude = in_activity.latitude
    if in_activity.longitude is not None:
        activity.longitude = in_activity.longitude

    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    return activity


def delete(activity_id: UUID, current_user: User, db_session: Session) -> Activity:
    activity = db_session.get(Activity, activity_id)
    if not activity:
        raise NotFoundError()

    store = db_session.get(Store, activity.owner_store_id)
    if not store:
        raise NotFoundError()
    if store.owner_user_id != current_user.id:
        raise PermissionDeniedError()

    db_session.delete(activity)
    db_session.commit()
    return activity
