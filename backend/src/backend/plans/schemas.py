from pydantic import BaseModel
from uuid import UUID

from backend.plans.models import Plan


class PlanItemSchema(BaseModel):
    activity_id: UUID


class PlanCreateRequest(BaseModel):
    name: str
    description: str
    details: list[PlanItemSchema]


class PlanReadResponse(BaseModel):
    id: UUID
    name: str
    description: str
    owner_user_id: UUID
    details: list[PlanItemSchema]

    @classmethod
    def from_plan(cls, plan: Plan) -> "PlanReadResponse":
        return cls(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            owner_user_id=plan.owner_user_id,
            details=[
                PlanItemSchema(activity_id=item.activity_id)
                for item in sorted(plan.items, key=lambda i: i.position)
            ],
        )


class PlanUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    items: list[PlanItemSchema] | None = None
