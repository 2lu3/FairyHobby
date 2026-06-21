"""activity_reviews エンドポイントのテスト。"""

from sqlmodel import Session

from backend.activity_reviews.models import ActivityReview
from backend.activities.models import Activity, ActivityImage
from backend.stores.models import Store
from backend.users.models import User


async def test_create_activity_review(client, db_session, firebase_uid, logged_in_user):
    """POST /activity-reviews/ でレビューを作成する。"""
    activity = _seed_activity(db_session, owner_user=logged_in_user)
    payload = {"text": "Great experience!", "activity_id": str(activity.id)}
    res = await client.post("/activity-reviews/", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["text"] == "Great experience!"
    assert body["activity_id"] == str(activity.id)
    assert body["owner_user_id"] == str(logged_in_user.id)

    created = db_session.get(ActivityReview, body["id"])
    assert created is not None
    assert created.text == "Great experience!"
    assert created.activity_id == activity.id


async def test_get_activity_review(client, db_session, firebase_uid):
    """GET /activity-reviews/{id} がレビューを返す。"""
    review = _seed_activity_review(
        db_session, firebase_uid=firebase_uid, text="Nice activity!"
    )
    res = await client.get(f"/activity-reviews/{review.id}")
    assert res.status_code == 200
    body = res.json()
    assert body["text"] == "Nice activity!"
    assert body["id"] == str(review.id)
    assert body["activity_id"] == str(review.activity_id)
    assert body["owner_user_id"] == str(review.owner_user_id)


async def test_update_activity_review(client, db_session, firebase_uid):
    """PATCH /activity-reviews/{id} がレビューを更新する。"""
    review = _seed_activity_review(
        db_session, firebase_uid=firebase_uid, text="Original review"
    )
    res = await client.patch(
        f"/activity-reviews/{review.id}",
        json={"text": "Updated review"},
    )
    assert res.status_code == 200
    assert res.json()["text"] == "Updated review"


async def test_delete_activity_review(client, db_session, firebase_uid):
    """DELETE /activity-reviews/{id} がレビューを削除する。"""
    review = _seed_activity_review(
        db_session, firebase_uid=firebase_uid, text="To be deleted"
    )
    res = await client.delete(f"/activity-reviews/{review.id}")
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == str(review.id)
    assert body["text"] == "To be deleted"
    assert body["activity_id"] == str(review.activity_id)
    assert body["owner_user_id"] == str(review.owner_user_id)
    assert db_session.get(ActivityReview, review.id) is None


def _seed_user(session: Session, **overrides) -> User:
    """テスト用ユーザーを 1 件作成して返す。"""
    defaults = dict(
        firebase_uid="seed-uid",
        email="seed@example.com",
        display_name="Seed",
        icon="🙂",
        is_admin=False,
    )
    defaults.update(overrides)
    user = User(**defaults)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_store(session: Session, owner_user: User | None = None, **overrides) -> Store:
    """テスト用ストアを 1 件作成して返す。"""
    if owner_user is None:
        user = _seed_user(
            session,
            firebase_uid=overrides.pop("firebase_uid", "test-firebase-uid"),
            email=overrides.pop("email", "test@example.com"),
            display_name=overrides.pop("display_name", "Test User"),
            icon=overrides.pop("icon", "🙂"),
            is_admin=overrides.pop("is_admin", False),
        )
    else:
        user = owner_user
        for key in ("firebase_uid", "email", "display_name", "icon", "is_admin"):
            overrides.pop(key, None)
    store = Store(
        name=overrides.get("name", "New Store"),
        description=overrides.get("description", "New Store Description"),
        owner_user_id=user.id,
    )
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def _seed_activity(
    session: Session, owner_user: User | None = None, **overrides
) -> Activity:
    """テスト用アクティビティを 1 件作成して返す。"""
    store = _seed_store(
        session,
        owner_user=owner_user,
        firebase_uid=overrides.pop("firebase_uid", "test-firebase-uid"),
        email=overrides.pop("email", "test@example.com"),
        display_name=overrides.pop("display_name", "Test User"),
        icon=overrides.pop("icon", "🙂"),
        is_admin=overrides.pop("is_admin", False),
        name=overrides.pop("store_name", "New Store"),
        description=overrides.pop("store_description", "New Store Description"),
    )
    image_urls = overrides.pop("image_urls", ["https://example.com/1.jpg"])
    activity = Activity(
        name=overrides.get("name", "New Activity"),
        description=overrides.get("description", "New Activity Description"),
        price=overrides.get("price", 1000),
        duration_minutes=overrides.get("duration_minutes", 60),
        owner_store_id=store.id,
        address=overrides.get("address"),
    )
    for image_url in image_urls:
        activity.images.append(ActivityImage(image_url=image_url))
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


def _seed_activity_review(session: Session, **overrides) -> ActivityReview:
    """テスト用アクティビティレビューを 1 件作成して返す。"""
    owner_user = overrides.pop("owner_user", None)
    if owner_user is None:
        owner_user = _seed_user(
            session,
            firebase_uid=overrides.pop("firebase_uid", "test-firebase-uid"),
            email=overrides.pop("email", "test@example.com"),
            display_name=overrides.pop("display_name", "Test User"),
            icon=overrides.pop("icon", "🙂"),
            is_admin=overrides.pop("is_admin", False),
        )
    else:
        for key in ("firebase_uid", "email", "display_name", "icon", "is_admin"):
            overrides.pop(key, None)

    activity = overrides.pop("activity", None)
    if activity is None:
        store = _seed_store(session, owner_user=owner_user)
        image_urls = overrides.pop("image_urls", ["https://example.com/1.jpg"])
        activity = Activity(
            name=overrides.pop("activity_name", "New Activity"),
            description=overrides.pop(
                "activity_description", "New Activity Description"
            ),
            price=overrides.pop("price", 1000),
            duration_minutes=overrides.pop("duration_minutes", 60),
            owner_store_id=store.id,
            address=overrides.pop("address", None),
        )
        for image_url in image_urls:
            activity.images.append(ActivityImage(image_url=image_url))
        session.add(activity)
        session.commit()
        session.refresh(activity)

    review = ActivityReview(
        text=overrides.get("text", "Sample review"),
        activity_id=activity.id,
        owner_user_id=owner_user.id,
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return review
