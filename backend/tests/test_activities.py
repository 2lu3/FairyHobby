"""activities エンドポイントのテスト。"""

from uuid import uuid4

from sqlmodel import Session

from backend.activities.models import Activity, ActivityImage
from backend.stores.models import Store
from backend.users.models import User


async def test_create_activity(client, db_session, firebase_uid, logged_in_user):
    """POST /activities/ でアクティビティを作成する。"""
    store = _seed_store(db_session, owner_user=logged_in_user)
    payload = {
        "name": "New Activity",
        "description": "New Activity Description",
        "price": 1500,
        "duration_minutes": 90,
        "image_urls": ["https://example.com/1.jpg", "https://example.com/2.jpg"],
        "owner_store_id": str(store.id),
        "address": "Tokyo",
    }
    res = await client.post("/activities/", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "New Activity"
    assert body["description"] == "New Activity Description"
    assert body["price"] == 1500
    assert body["duration_minutes"] == 90
    assert body["image_urls"] == payload["image_urls"]
    assert body["owner_store_id"] == str(store.id)
    assert body["address"] == "Tokyo"
    assert body["reviews"] == []

    created = db_session.get(Activity, body["id"])
    assert created is not None
    assert created.owner_store_id == store.id
    assert [img.image_url for img in created.images] == payload["image_urls"]


async def test_create_activity_store_not_found(client, db_session, firebase_uid):
    """存在しないストアへの作成は 404。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    res = await client.post(
        "/activities/",
        json={
            "name": "New Activity",
            "description": "Description",
            "price": 1000,
            "duration_minutes": 60,
            "image_urls": [],
            "owner_store_id": str(uuid4()),
            "address": None,
        },
    )
    assert res.status_code == 404


async def test_create_activity_forbidden_when_not_store_owner(
    client, db_session, firebase_uid
):
    """ストアのオーナー以外の作成は 403。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    store = _seed_store(
        db_session,
        firebase_uid="other-uid",
        email="other@example.com",
        name="Other Store",
        description="Other Store Description",
    )
    res = await client.post(
        "/activities/",
        json={
            "name": "Hacked Activity",
            "description": "Hacked",
            "price": 1000,
            "duration_minutes": 60,
            "image_urls": [],
            "owner_store_id": str(store.id),
            "address": None,
        },
    )
    assert res.status_code == 403


async def test_get_activity(client, db_session, firebase_uid):
    """GET /activities/{id} がアクティビティを返す。"""
    activity = _seed_activity(
        db_session,
        firebase_uid=firebase_uid,
        name="New Activity",
        description="New Activity Description",
    )
    res = await client.get(f"/activities/{activity.id}")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "New Activity"
    assert body["description"] == "New Activity Description"
    assert body["price"] == 1000
    assert body["duration_minutes"] == 60
    assert body["id"] == str(activity.id)
    assert body["image_urls"] == ["https://example.com/1.jpg"]
    assert body["reviews"] == []


async def test_get_activity_not_found(client, db_session, firebase_uid):
    """存在しないアクティビティは 404。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    res = await client.get(f"/activities/{uuid4()}")
    assert res.status_code == 404


async def test_update_activity(client, db_session, firebase_uid):
    """PATCH /activities/{id} がアクティビティを更新する。"""
    activity = _seed_activity(
        db_session,
        firebase_uid=firebase_uid,
        name="New Activity",
        description="New Activity Description",
    )
    res = await client.patch(
        f"/activities/{activity.id}",
        json=_update_payload(
            name="Updated Activity",
            description="Updated Description",
            price=2000,
            duration_minutes=120,
            address="Osaka",
        ),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Updated Activity"
    assert body["description"] == "Updated Description"
    assert body["price"] == 2000
    assert body["duration_minutes"] == 120
    assert body["address"] == "Osaka"


async def test_update_activity_not_found(client, db_session, firebase_uid):
    """存在しないアクティビティの更新は 404。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    res = await client.patch(
        f"/activities/{uuid4()}",
        json=_update_payload(
            name="Updated Activity",
            description="Updated Description",
        ),
    )
    assert res.status_code == 404


async def test_update_activity_forbidden_when_not_owner(
    client, db_session, firebase_uid
):
    """ストアのオーナー以外の更新は 403。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    activity = _seed_activity(
        db_session,
        firebase_uid="other-uid",
        email="other@example.com",
        name="Other Activity",
        description="Other Description",
    )
    res = await client.patch(
        f"/activities/{activity.id}",
        json=_update_payload(name="Hacked Activity", description="Hacked"),
    )
    assert res.status_code == 403


async def test_delete_activity(client, db_session, firebase_uid):
    """DELETE /activities/{id} がアクティビティを削除する。"""
    activity = _seed_activity(
        db_session,
        firebase_uid=firebase_uid,
        name="New Activity",
        description="New Activity Description",
    )
    res = await client.delete(f"/activities/{activity.id}")
    assert res.status_code == 200
    assert res.json()["id"] == str(activity.id)
    assert db_session.get(Activity, activity.id) is None


async def test_delete_activity_not_found(client, db_session, firebase_uid):
    """存在しないアクティビティの削除は 404。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    res = await client.delete(f"/activities/{uuid4()}")
    assert res.status_code == 404


async def test_delete_activity_forbidden_when_not_owner(
    client, db_session, firebase_uid
):
    """ストアのオーナー以外の削除は 403。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    activity = _seed_activity(
        db_session,
        firebase_uid="other-uid",
        email="other@example.com",
        name="Other Activity",
        description="Other Description",
    )
    res = await client.delete(f"/activities/{activity.id}")
    assert res.status_code == 403
    assert db_session.get(Activity, activity.id) is not None


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


def _update_payload(**overrides) -> dict:
    """ActivityUpdateRequest の全フィールドを含む PATCH 用ペイロード。"""
    defaults = {
        "name": None,
        "description": None,
        "price": None,
        "duration_minutes": None,
        "image_urls": None,
        "address": None,
        "preference_text": None,
    }
    defaults.update(overrides)
    return defaults


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


def _seed_activity(session: Session, **overrides) -> Activity:
    """テスト用アクティビティを 1 件作成して返す。"""
    store = _seed_store(
        session,
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
