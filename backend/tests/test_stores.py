"""stores エンドポイントのテスト。"""

from uuid import uuid4

from sqlmodel import Session

from backend.stores.models import Store
from backend.users.models import User


async def test_create_store(client, db_session, firebase_uid, logged_in_user):
    """POST /stores/ でストアを作成する。"""
    res = await client.post(
        "/stores/", json={"name": "New Store", "description": "New Store Description"}
    )
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "New Store"
    assert body["description"] == "New Store Description"
    assert body["owner_user_id"] == str(logged_in_user.id)

    created = db_session.get(Store, body["id"])
    assert created is not None
    assert created.owner_user_id == logged_in_user.id


async def test_get_store(client, db_session, firebase_uid):
    """GET /stores/{id} がストアを返す。"""
    store = _seed_store(
        db_session,
        firebase_uid=firebase_uid,
        name="New Store",
        description="New Store Description",
    )
    res = await client.get(f"/stores/{store.id}")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "New Store"
    assert body["description"] == "New Store Description"
    assert body["id"] == str(store.id)


async def test_get_store_not_found(client, db_session, firebase_uid):
    """存在しないストアは 404。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    res = await client.get(f"/stores/{uuid4()}")
    assert res.status_code == 404


async def test_update_store(client, db_session, firebase_uid):
    """PATCH /stores/{id} がストアを更新する。"""
    store = _seed_store(
        db_session,
        firebase_uid=firebase_uid,
        name="New Store",
        description="New Store Description",
    )
    res = await client.patch(
        f"/stores/{store.id}",
        json={"name": "Updated Store", "description": "Updated Store Description"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Updated Store"
    assert body["description"] == "Updated Store Description"


async def test_update_store_not_found(client, db_session, firebase_uid):
    """存在しないストアの更新は 404。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    res = await client.patch(
        f"/stores/{uuid4()}",
        json={"name": "Updated Store", "description": "Updated Store Description"},
    )
    assert res.status_code == 404


async def test_update_store_forbidden_when_not_owner(client, db_session, firebase_uid):
    """オーナー以外の更新は 403。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    store = _seed_store(
        db_session,
        firebase_uid="other-uid",
        email="other@example.com",
        name="Other Store",
        description="Other Store Description",
    )
    res = await client.patch(
        f"/stores/{store.id}",
        json={"name": "Hacked Store", "description": "Hacked"},
    )
    assert res.status_code == 403


async def test_delete_store(client, db_session, firebase_uid):
    """DELETE /stores/{id} がストアを削除する。"""
    store = _seed_store(
        db_session,
        firebase_uid=firebase_uid,
        name="New Store",
        description="New Store Description",
    )
    res = await client.delete(f"/stores/{store.id}")
    assert res.status_code == 200
    assert res.json()["id"] == str(store.id)
    assert db_session.get(Store, store.id) is None


async def test_delete_store_not_found(client, db_session, firebase_uid):
    """存在しないストアの削除は 404。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    res = await client.delete(f"/stores/{uuid4()}")
    assert res.status_code == 404


async def test_delete_store_forbidden_when_not_owner(client, db_session, firebase_uid):
    """オーナー以外の削除は 403。"""
    _seed_user(db_session, firebase_uid=firebase_uid)
    store = _seed_store(
        db_session,
        firebase_uid="other-uid",
        email="other@example.com",
        name="Other Store",
        description="Other Store Description",
    )
    res = await client.delete(f"/stores/{store.id}")
    assert res.status_code == 403
    assert db_session.get(Store, store.id) is not None


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


def _seed_store(session: Session, **overrides) -> Store:
    """テスト用ストアを 1 件作成して返す。"""
    user = _seed_user(
        session,
        firebase_uid=overrides.pop("firebase_uid", "test-firebase-uid"),
        email=overrides.pop("email", "test@example.com"),
        display_name=overrides.pop("display_name", "Test User"),
        icon=overrides.pop("icon", "🙂"),
        is_admin=overrides.pop("is_admin", False),
    )
    store = Store(
        name=overrides.get("name", "New Store"),
        description=overrides.get("description", "New Store Description"),
        owner_user_id=user.id,
    )
    session.add(store)
    session.commit()
    session.refresh(store)
    return store
