"""users エンドポイントのサンプルテスト。

このファイルはテストハーネスの使い方の見本:
  - db_session   : rollback で分離された実 Postgres セッション（テストデータ投入用）
  - client       : get_session / get_firebase_uid を差し替え済みの ASGI クライアント
  - firebase_uid : テストで「ログイン中」として扱う firebase uid
"""

from sqlmodel import Session

from backend.users.models import User


async def test_create_user(client, db_session, firebase_uid, monkeypatch):
    """POST /users/ でユーザーを作成する。

    create_user サービスは Firebase からメールを引くため、その部分だけ monkeypatch する。
    （get_firebase_uid はクライアント側のオーバーライドで差し替え済み）
    """
    monkeypatch.setattr(
        "backend.users.service.get_email_from_firebase",
        lambda firebase_uid: "new@example.com",
    )

    res = await client.post("/users", json={"display_name": "New User"})

    assert res.status_code == 201
    body = res.json()
    assert body["display_name"] == "New User"

    # 実際に DB に入っていることを確認
    created = db_session.get(User, body["id"])
    assert created is not None
    assert created.email == "new@example.com"
    assert created.firebase_uid == firebase_uid


async def test_get_user_me_returns_logged_in_user(client, db_session, firebase_uid):
    """GET /users/me が、firebase_uid に対応するログイン済みユーザーを返す。"""
    user = _seed_user(
        db_session, firebase_uid=firebase_uid, email="me@example.com", display_name="Me"
    )

    res = await client.get("/users/me")

    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "me@example.com"
    assert body["display_name"] == "Me"
    assert body["id"] == str(user.id)


async def test_get_user_by_id(client, db_session, firebase_uid):
    """GET /users/{id} が他ユーザーの公開情報を返す。"""
    # ログイン中ユーザー（get_firebase_uid のオーバーライドに対応）
    _seed_user(db_session, firebase_uid=firebase_uid, email="me@example.com")
    # 取得対象の別ユーザー
    other = _seed_user(
        db_session,
        firebase_uid="other-uid",
        email="other@example.com",
        display_name="Other",
    )

    res = await client.get(f"/users/{other.id}")

    assert res.status_code == 200
    assert res.json()["display_name"] == "Other"


async def test_get_user_me_not_found_when_user_absent(client):
    """DB にユーザーがいなければ 404。"""
    res = await client.get("/users/me")
    assert res.status_code == 404


async def test_update_user(client, db_session, firebase_uid):
    """PATCH /users/{id} がユーザーを更新する。"""
    user = _seed_user(
        db_session, firebase_uid=firebase_uid, email="me@example.com", display_name="Me"
    )
    res = await client.patch(f"/users/{user.id}", json={"display_name": "Updated"})
    assert res.status_code == 200
    assert res.json()["display_name"] == "Updated"


async def test_delete_user(client, db_session, firebase_uid):
    """DELETE /users/{id} がユーザーを削除する。"""
    user = _seed_user(
        db_session, firebase_uid=firebase_uid, email="me@example.com", display_name="Me"
    )
    res = await client.delete(f"/users/{user.id}")
    assert res.status_code == 200
    assert res.json()["id"] == str(user.id)
    assert db_session.get(User, user.id) is None


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
