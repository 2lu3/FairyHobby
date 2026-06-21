import logging
from uuid import UUID

from sqlmodel import Session, select

from backend.exceptions import NotFoundError, PermissionDeniedError
from backend.plan_histories.models import PlanHistory
from backend.plan_histories.schemas import (
    PlanHistoryCreateRequest,
    PlanHistoryUpdateRequest,
)
from backend.plans.models import Plan
from backend.users.models import User

logger = logging.getLogger(__name__)


def _validate_plan_exists(plan_id: UUID, db_session: Session) -> None:
    plan = db_session.get(Plan, plan_id)
    if not plan:
        raise NotFoundError()


def _ensure_owner_or_admin(plan_history: PlanHistory, current_user: User) -> None:
    if plan_history.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDeniedError()


def create(
    in_plan_history: PlanHistoryCreateRequest,
    current_user: User,
    db_session: Session,
) -> PlanHistory:
    _validate_plan_exists(in_plan_history.plan_id, db_session)

    plan_history = PlanHistory(
        user_id=current_user.id,
        plan_id=in_plan_history.plan_id,
    )
    db_session.add(plan_history)
    db_session.commit()
    db_session.refresh(plan_history)
    logger.info("Created plan_history %s by %s", plan_history.id, current_user.id)
    return plan_history


def get(plan_history_id: UUID, current_user: User, db_session: Session) -> PlanHistory:
    plan_history = db_session.get(PlanHistory, plan_history_id)
    if not plan_history:
        raise NotFoundError()
    _ensure_owner_or_admin(plan_history, current_user)
    return plan_history


def get_all(current_user: User, db_session: Session) -> list[PlanHistory]:
    """ログイン中ユーザーのPlan履歴を新しい順で返す。"""
    plan_histories = db_session.exec(
        select(PlanHistory)
        .where(PlanHistory.user_id == current_user.id)
        .order_by(PlanHistory.created_at.desc())
    ).all()
    return plan_histories


def update(
    plan_history_id: UUID,
    in_plan_history: PlanHistoryUpdateRequest,
    current_user: User,
    db_session: Session,
) -> PlanHistory:
    plan_history = db_session.get(PlanHistory, plan_history_id)
    if not plan_history:
        raise NotFoundError()
    _ensure_owner_or_admin(plan_history, current_user)

    if in_plan_history.plan_id is not None:
        _validate_plan_exists(in_plan_history.plan_id, db_session)
        plan_history.plan_id = in_plan_history.plan_id

    db_session.add(plan_history)
    db_session.commit()
    db_session.refresh(plan_history)
    logger.info("Updated plan_history %s by %s", plan_history.id, current_user.id)
    return plan_history


def delete(
    plan_history_id: UUID, current_user: User, db_session: Session
) -> PlanHistory:
    plan_history = db_session.get(PlanHistory, plan_history_id)
    if not plan_history:
        raise NotFoundError()
    _ensure_owner_or_admin(plan_history, current_user)

    db_session.delete(plan_history)
    db_session.commit()
    logger.info("Deleted plan_history %s by %s", plan_history_id, current_user.id)
    return plan_history
