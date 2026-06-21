"""plan_histories エンドポイントとサービスのテスト。"""

from uuid import uuid4

import pytest
from sqlmodel import Session

from backend.exceptions import NotFoundError, PermissionDeniedError
from backend.plan_histories.models import PlanHistory
from backend.plan_histories.schemas import (
    PlanHistoryCreateRequest,
    PlanHistoryUpdateRequest,
)
from backend.plan_histories.service import (
    create,
    delete,
    get,
    get_all,
    update,
)
from backend.plans.models import Plan
from backend.users.models import User


def test_create(db_session: Session, logged_in_user: User):
    """create が履歴を保存し、ログインユーザーに紐づける。"""
    plan = _seed_plan(db_session)
    request = PlanHistoryCreateRequest(plan_id=plan.id)

    plan_history = create(request, logged_in_user, db_session)

    assert plan_history.user_id == logged_in_user.id
    assert plan_history.plan_id == plan.id

    stored = db_session.get(PlanHistory, plan_history.id)
    assert stored is not None


def test_create_plan_not_found(db_session: Session, logged_in_user: User):
    """存在しないPlanに対する履歴作成は NotFoundError。"""
    request = PlanHistoryCreateRequest(plan_id=uuid4())

    with pytest.raises(NotFoundError):
        create(request, logged_in_user, db_session)


def test_get_success(db_session: Session, logged_in_user: User):
    """所有者は自分の履歴を取得できる。"""
    plan = _seed_plan(db_session)
    plan_history = _seed_plan_history(db_session, logged_in_user, plan)

    result = get(plan_history.id, logged_in_user, db_session)

    assert result.id == plan_history.id


def test_get_not_found(db_session: Session, logged_in_user: User):
    """存在しない履歴は NotFoundError。"""
    with pytest.raises(NotFoundError):
        get(uuid4(), logged_in_user, db_session)


def test_get_forbidden(db_session: Session, logged_in_user: User):
    """他ユーザーの履歴は PermissionDeniedError。"""
    other_user = _seed_user(
        db_session, firebase_uid="other-uid", email="other@example.com"
    )
    plan = _seed_plan(db_session)
    plan_history = _seed_plan_history(db_session, other_user, plan)

    with pytest.raises(PermissionDeniedError):
        get(plan_history.id, logged_in_user, db_session)


def test_get_all_returns_only_own(db_session: Session, logged_in_user: User):
    """get_all はログインユーザー自身の履歴のみ返す。"""
    other_user = _seed_user(
        db_session, firebase_uid="other-uid", email="other@example.com"
    )
    plan = _seed_plan(db_session)
    own_first = _seed_plan_history(db_session, logged_in_user, plan)
    own_second = _seed_plan_history(db_session, logged_in_user, plan)
    _seed_plan_history(db_session, other_user, plan)

    histories = get_all(logged_in_user, db_session)

    history_ids = {history.id for history in histories}
    assert history_ids == {own_first.id, own_second.id}


def test_update(db_session: Session, logged_in_user: User):
    """update が plan_id を差し替える。"""
    plan = _seed_plan(db_session)
    other_plan = _seed_plan(db_session, name="Other Plan")
    plan_history = _seed_plan_history(db_session, logged_in_user, plan)

    updated = update(
        plan_history.id,
        PlanHistoryUpdateRequest(plan_id=other_plan.id),
        logged_in_user,
        db_session,
    )

    assert updated.plan_id == other_plan.id


def test_update_forbidden(db_session: Session, logged_in_user: User):
    """他ユーザーの履歴は更新できない。"""
    other_user = _seed_user(
        db_session, firebase_uid="other-uid", email="other@example.com"
    )
    plan = _seed_plan(db_session)
    plan_history = _seed_plan_history(db_session, other_user, plan)

    with pytest.raises(PermissionDeniedError):
        update(
            plan_history.id,
            PlanHistoryUpdateRequest(plan_id=plan.id),
            logged_in_user,
            db_session,
        )


def test_delete(db_session: Session, logged_in_user: User):
    """delete が履歴を削除する。"""
    plan = _seed_plan(db_session)
    plan_history = _seed_plan_history(db_session, logged_in_user, plan)

    delete(plan_history.id, logged_in_user, db_session)

    assert db_session.get(PlanHistory, plan_history.id) is None


def test_delete_forbidden(db_session: Session, logged_in_user: User):
    """他ユーザーの履歴は削除できない。"""
    other_user = _seed_user(
        db_session, firebase_uid="other-uid", email="other@example.com"
    )
    plan = _seed_plan(db_session)
    plan_history = _seed_plan_history(db_session, other_user, plan)

    with pytest.raises(PermissionDeniedError):
        delete(plan_history.id, logged_in_user, db_session)


async def test_create_plan_history_endpoint(client, db_session, logged_in_user):
    """POST /plan-histories で履歴を作成する。"""
    plan = _seed_plan(db_session)

    res = await client.post("/plan-histories", json={"plan_id": str(plan.id)})

    assert res.status_code == 201
    body = res.json()
    assert body["plan_id"] == str(plan.id)
    assert body["user_id"] == str(logged_in_user.id)

    created = db_session.get(PlanHistory, body["id"])
    assert created is not None


async def test_create_plan_history_endpoint_plan_not_found(
    client, db_session, logged_in_user
):
    """存在しないPlanは 404。"""
    res = await client.post("/plan-histories", json={"plan_id": str(uuid4())})
    assert res.status_code == 404


async def test_list_plan_histories_endpoint(client, db_session, logged_in_user):
    """GET /plan-histories でログインユーザーの履歴一覧を返す。"""
    other_user = _seed_user(
        db_session, firebase_uid="other-uid", email="other@example.com"
    )
    plan = _seed_plan(db_session)
    own = _seed_plan_history(db_session, logged_in_user, plan)
    _seed_plan_history(db_session, other_user, plan)

    res = await client.get("/plan-histories")

    assert res.status_code == 200
    body = res.json()
    assert [item["id"] for item in body] == [str(own.id)]


async def test_get_plan_history_endpoint_forbidden(client, db_session, logged_in_user):
    """他ユーザーの履歴取得は 403。"""
    other_user = _seed_user(
        db_session, firebase_uid="other-uid", email="other@example.com"
    )
    plan = _seed_plan(db_session)
    plan_history = _seed_plan_history(db_session, other_user, plan)

    res = await client.get(f"/plan-histories/{plan_history.id}")
    assert res.status_code == 403


async def test_delete_plan_history_endpoint(client, db_session, logged_in_user):
    """DELETE /plan-histories/{id} で履歴を削除する。"""
    plan = _seed_plan(db_session)
    plan_history = _seed_plan_history(db_session, logged_in_user, plan)

    res = await client.request("DELETE", f"/plan-histories/{plan_history.id}")

    assert res.status_code == 200
    assert res.json()["id"] == str(plan_history.id)
    assert db_session.get(PlanHistory, plan_history.id) is None


def _seed_user(session: Session, **overrides) -> User:
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


def _seed_plan(session: Session, **overrides) -> Plan:
    plan = Plan(
        name=overrides.get("name", "Test Plan"),
        description=overrides.get("description", "Test Plan Description"),
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def _seed_plan_history(session: Session, user: User, plan: Plan) -> PlanHistory:
    plan_history = PlanHistory(user_id=user.id, plan_id=plan.id)
    session.add(plan_history)
    session.commit()
    session.refresh(plan_history)
    return plan_history
