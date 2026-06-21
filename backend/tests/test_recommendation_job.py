"""recommendation_job エンドポイントとサービスのテスト。"""

from datetime import date
from uuid import uuid4

import pytest
from sqlmodel import Session

from backend.activities.models import Activity, ActivityImage
from backend.fairies.models import Fairy
from backend.plans.models import Plan
from backend.recommendation_job.models import RecommendationJob, RecommendationStatus
from backend.recommendation_job.schemas import RecommendationJobCreateRequest
from backend.recommendation_job.service import (
    _mark_failed,
    _save_result,
    _start_calculation,
    create_job,
    get_job_for_user,
)
from backend.recommendation_job.worker import Optimizer
from backend.stores.models import Store
from backend.users.models import User


@pytest.fixture
def mock_generate_recommendation(monkeypatch):
    """POST 時の background task で最適化処理を走らせない。"""

    def _noop(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "backend.recommendation_job.router.generate_recommendation", _noop
    )


@pytest.fixture(autouse=True)
def mock_plan_name_generation(monkeypatch):
    """プラン名・説明の LLM 生成をテスト中は固定値に差し替える。"""

    def _fake(activities, fairy):
        return "テストプラン", "テスト用のプラン説明"

    monkeypatch.setattr(
        "backend.recommendation_job.service._generate_plan_name_and_description",
        _fake,
    )


def test_create_job(db_session: Session, logged_in_user: User):
    """create_job がジョブを DB に保存する。"""
    fairy = _seed_fairy(db_session)
    request = RecommendationJobCreateRequest(
        fairy_id=fairy.id,
        date=date(2026, 6, 21),
        budget=10000,
    )

    job = create_job(request, logged_in_user, db_session)

    assert job.user_id == logged_in_user.id
    assert job.fairy_id == fairy.id
    assert job.date == date(2026, 6, 21)
    assert job.budget == 10000
    assert job.status == RecommendationStatus.PENDING
    assert job.plan_id is None

    stored = db_session.get(RecommendationJob, job.id)
    assert stored is not None


def test_get_job_for_user_success(db_session: Session, logged_in_user: User):
    """所有者は自分のジョブを取得できる。"""
    fairy = _seed_fairy(db_session)
    job = _seed_recommendation_job(db_session, logged_in_user, fairy)

    result = get_job_for_user(job.id, logged_in_user, db_session)

    assert result.id == job.id


def test_get_job_for_user_not_found(db_session: Session, logged_in_user: User):
    """存在しないジョブは NotFoundError。"""
    from backend.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        get_job_for_user(uuid4(), logged_in_user, db_session)


def test_get_job_for_user_forbidden(db_session: Session, logged_in_user: User):
    """他ユーザーのジョブは PermissionDeniedError。"""
    from backend.exceptions import PermissionDeniedError

    other_user = _seed_user(
        db_session, firebase_uid="other-uid", email="other@example.com"
    )
    fairy = _seed_fairy(db_session)
    job = _seed_recommendation_job(db_session, other_user, fairy)

    with pytest.raises(PermissionDeniedError):
        get_job_for_user(job.id, logged_in_user, db_session)


def test_generate_recommendation_success(db_session: Session, logged_in_user: User):
    """最適化成功時に COMPLETED と plan_id が設定される。"""
    fairy = _seed_fairy(db_session, embeddings=[1.0, 0.0, 0.0])
    _seed_activity(
        db_session,
        name="Similar Activity",
        price=2000,
        duration_minutes=90,
        embeddings=[1.0, 0.0, 0.0],
    )
    _seed_activity(
        db_session,
        name="Different Activity",
        price=5000,
        duration_minutes=120,
        embeddings=[0.0, 1.0, 0.0],
    )
    job = _seed_recommendation_job(
        db_session,
        logged_in_user,
        fairy,
        budget=10000,
    )

    recommendation_job = _start_calculation(job.id, db_session)
    assert recommendation_job is not None
    optimizer = Optimizer(recommendation_job, db_session)
    optimizer.build_model()
    activities = optimizer.run()
    _save_result(job.id, activities, db_session)

    db_session.refresh(job)
    assert job.status == RecommendationStatus.COMPLETED
    assert job.plan_id is not None
    plan = db_session.get(Plan, job.plan_id)
    assert plan is not None
    assert plan.name == "テストプラン"
    assert plan.description == "テスト用のプラン説明"
    assert len(plan.items) >= 1


def test_generate_recommendation_fails_on_optimizer_error(
    db_session: Session, logged_in_user: User, monkeypatch
):
    """最適化失敗時は FAILED になる。"""
    fairy = _seed_fairy(db_session)
    job = _seed_recommendation_job(db_session, logged_in_user, fairy)

    def _raise(_self):
        raise RuntimeError("optimization failed")

    monkeypatch.setattr(Optimizer, "build_model", _raise)

    recommendation_job = _start_calculation(job.id, db_session)
    assert recommendation_job is not None
    optimizer = Optimizer(recommendation_job, db_session)

    with pytest.raises(RuntimeError, match="optimization failed"):
        optimizer.build_model()
    _mark_failed(job.id, db_session)

    db_session.refresh(job)
    assert job.status == RecommendationStatus.FAILED


def test_optimizer_raises_when_fairy_missing(db_session: Session, logged_in_user: User):
    """妖精が存在しない場合 Optimizer は ValueError を投げる。"""
    job = RecommendationJob(
        user_id=logged_in_user.id,
        fairy_id=uuid4(),
        date=date(2026, 6, 21),
        budget=10000,
    )

    optimizer = Optimizer(job, db_session)

    with pytest.raises(ValueError, match="Fairy not found"):
        optimizer.build_model()


def test_generate_recommendation_skips_non_pending(
    db_session: Session, logged_in_user: User
):
    """PENDING 以外のジョブは再計算しない。"""
    fairy = _seed_fairy(db_session)
    existing_plan = Plan(name="Existing Plan", description="Already created")
    db_session.add(existing_plan)
    db_session.commit()
    db_session.refresh(existing_plan)
    job = _seed_recommendation_job(
        db_session,
        logged_in_user,
        fairy,
        status=RecommendationStatus.COMPLETED,
        plan_id=existing_plan.id,
    )

    result = _start_calculation(job.id, db_session)

    assert result is None
    db_session.refresh(job)
    assert job.status == RecommendationStatus.COMPLETED
    assert job.plan_id == existing_plan.id


def test_optimizer_selects_within_budget(db_session: Session, logged_in_user: User):
    """Optimizer が予算内で類似度の高いアクティビティを選ぶ。"""
    fairy = _seed_fairy(db_session, embeddings=[1.0, 0.0])
    similar = _seed_activity(
        db_session,
        name="Similar",
        price=3000,
        duration_minutes=60,
        embeddings=[1.0, 0.0],
    )
    _seed_activity(
        db_session,
        name="Dissimilar",
        price=3000,
        duration_minutes=60,
        embeddings=[0.0, 1.0],
    )
    job = _seed_recommendation_job(
        db_session,
        logged_in_user,
        fairy,
        budget=4000,
    )

    optimizer = Optimizer(job, db_session)
    optimizer.build_model()
    activities = optimizer.run()

    selected_ids = {activity.id for activity in activities}
    assert similar.id in selected_ids
    assert sum(activity.price for activity in activities) <= job.budget


async def test_create_recommendation_job(
    client, db_session, logged_in_user, mock_generate_recommendation
):
    """POST /recommendation/jobs でジョブを作成する。"""
    fairy = _seed_fairy(db_session)
    payload = {
        "fairy_id": str(fairy.id),
        "date": "2026-06-21",
        "budget": 10000,
    }

    res = await client.post("/recommendation/jobs", json=payload)

    assert res.status_code == 201
    body = res.json()
    assert body["status"] == RecommendationStatus.PENDING.value
    assert body["plan_id"] is None

    created = db_session.get(RecommendationJob, body["id"])
    assert created is not None
    assert created.fairy_id == fairy.id
    assert created.user_id == logged_in_user.id


async def test_create_recommendation_job_not_found_when_user_absent(
    client, mock_generate_recommendation
):
    """DB にユーザーがいなければ 404。"""
    fairy_id = uuid4()
    res = await client.post(
        "/recommendation/jobs",
        json={
            "fairy_id": str(fairy_id),
            "date": "2026-06-21",
            "budget": 10000,
        },
    )
    assert res.status_code == 404


async def test_get_recommendation_job_status(client, db_session, logged_in_user):
    """GET /recommendation/jobs/{id}/status がステータスを返す。"""
    fairy = _seed_fairy(db_session)
    plan = Plan(name="Completed Plan", description="Done")
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    job = _seed_recommendation_job(
        db_session,
        logged_in_user,
        fairy,
        status=RecommendationStatus.COMPLETED,
        plan_id=plan.id,
    )

    res = await client.get(f"/recommendation/jobs/{job.id}/status")

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == RecommendationStatus.COMPLETED.value
    assert body["plan_id"] == str(plan.id)


async def test_get_recommendation_job_status_not_found(
    client, db_session, logged_in_user
):
    """存在しないジョブは 404。"""
    res = await client.get(f"/recommendation/jobs/{uuid4()}/status")
    assert res.status_code == 404


async def test_get_recommendation_job_status_forbidden(
    client, db_session, logged_in_user
):
    """他ユーザーのジョブは 403。"""
    other_user = _seed_user(
        db_session, firebase_uid="other-uid", email="other@example.com"
    )
    fairy = _seed_fairy(db_session)
    job = _seed_recommendation_job(db_session, other_user, fairy)

    res = await client.get(f"/recommendation/jobs/{job.id}/status")
    assert res.status_code == 403


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


def _seed_store(session: Session, owner_user: User, **overrides) -> Store:
    store = Store(
        name=overrides.get("name", "Test Store"),
        description=overrides.get("description", "Test Store Description"),
        owner_user_id=owner_user.id,
    )
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


def _seed_fairy(session: Session, **overrides) -> Fairy:
    fairy = Fairy(
        name=overrides.get("name", f"fairy-{uuid4()}"),
        prompt=overrides.get("prompt", "Test fairy"),
        image_path=overrides.get("image_path", "fairies/test.png"),
        image_content_type=overrides.get("image_content_type", "image/png"),
        embeddings=overrides.get("embeddings", [1.0, 0.0, 0.0]),
    )
    session.add(fairy)
    session.commit()
    session.refresh(fairy)
    return fairy


def _seed_activity(session: Session, **overrides) -> Activity:
    user = _seed_user(
        session,
        firebase_uid=overrides.pop("firebase_uid", f"store-owner-{uuid4()}"),
        email=overrides.pop("email", f"owner-{uuid4()}@example.com"),
    )
    store = _seed_store(session, user)
    image_urls = overrides.pop("image_urls", ["https://example.com/1.jpg"])
    activity = Activity(
        name=overrides.get("name", "Test Activity"),
        description=overrides.get("description", "Test Activity Description"),
        price=overrides.get("price", 1000),
        duration_minutes=overrides.get("duration_minutes", 60),
        owner_store_id=store.id,
        address=overrides.get("address", "Tokyo"),
        embeddings=overrides.get("embeddings", [1.0, 0.0, 0.0]),
    )
    for image_url in image_urls:
        activity.images.append(ActivityImage(image_url=image_url))
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


def _seed_recommendation_job(
    session: Session,
    user: User,
    fairy: Fairy,
    **overrides,
) -> RecommendationJob:
    job = RecommendationJob(
        user_id=user.id,
        fairy_id=fairy.id,
        date=overrides.get("date", date(2026, 6, 21)),
        budget=overrides.get("budget", 10000),
        status=overrides.get("status", RecommendationStatus.PENDING),
        plan_id=overrides.get("plan_id"),
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job
