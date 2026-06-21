import logging
from uuid import UUID

from sqlmodel import Session

from backend.activities.models import Activity
from backend.exceptions import NotFoundError
from backend.plans.models import Plan, PlanItem
from backend.plans.schemas import PlanCreateRequest, PlanItemSchema, PlanUpdateRequest

logger = logging.getLogger(__name__)


def _validate_activities_exist(
    items: list[PlanItemSchema], db_session: Session
) -> None:
    for item in items:
        activity = db_session.get(Activity, item.activity_id)
        if not activity:
            raise NotFoundError()


def create(in_plan: PlanCreateRequest, db_session: Session) -> Plan:
    _validate_activities_exist(in_plan.details, db_session)

    plan = Plan(
        name=in_plan.name,
        description=in_plan.description,
    )
    for position, item in enumerate(in_plan.details):
        plan.items.append(
            PlanItem(
                position=position,
                activity_id=item.activity_id,
            )
        )

    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    logger.info("Created plan %s", plan.id)
    return plan


def get(plan_id: UUID, db_session: Session) -> Plan:
    plan = db_session.get(Plan, plan_id)
    if not plan:
        raise NotFoundError()
    return plan


def update(
    plan_id: UUID,
    in_plan: PlanUpdateRequest,
    db_session: Session,
) -> Plan:
    plan = db_session.get(Plan, plan_id)
    if not plan:
        raise NotFoundError()

    if in_plan.name is not None:
        plan.name = in_plan.name
    if in_plan.description is not None:
        plan.description = in_plan.description
    if in_plan.items is not None:
        _validate_activities_exist(in_plan.items, db_session)
        for existing in list(plan.items):
            db_session.delete(existing)
        plan.items.clear()
        for position, item in enumerate(in_plan.items):
            plan.items.append(
                PlanItem(
                    position=position,
                    activity_id=item.activity_id,
                )
            )

    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    logger.info("Updated plan %s", plan.id)
    return plan


def delete(plan_id: UUID, db_session: Session) -> Plan:
    plan = db_session.get(Plan, plan_id)
    if not plan:
        raise NotFoundError()

    db_session.delete(plan)
    db_session.commit()
    logger.info("Deleted plan %s", plan_id)
    return plan
