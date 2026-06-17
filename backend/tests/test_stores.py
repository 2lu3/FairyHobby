from uuid import uuid4
from sqlmodel import Session
from backend.stores.models import Store


async def test_create_store(client, db_session, firebase_uid, monkeypatch):
    monkeypatch.setattr(
        "backend.users.service.get_email_from_firebase",
        lambda firebase_uid: "new@example.com",
    )

    res = await client.post(
        "/stores/", json={"name": "New Store", "description": "New Store Description"}
    )
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "New Store"
    assert body["description"] == "New Store Description"


async def test_get_store(client, db_session, firebase_uid):
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


async def test_update_store(client, db_session, firebase_uid):
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


async def test_delete_store(client, db_session, firebase_uid):
    store = _seed_store(
        db_session,
        firebase_uid=firebase_uid,
        name="New Store",
        description="New Store Description",
    )
    res = await client.delete(f"/stores/{store.id}")
    assert res.status_code == 200
    assert db_session.get(Store, store.id) is None


def _seed_store(session: Session, **overrides) -> Store:
    store = Store(
        name="New Store",
        description="New Store Description",
        owner_user_id=overrides.get("owner_user_id", uuid4()),
    )
    session.add(store)
    session.commit()
    session.refresh(store)
    return store
