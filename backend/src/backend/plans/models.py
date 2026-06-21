from uuid import UUID

from sqlmodel import Field, Relationship

from backend.database import Base


class Plan(Base, table=True):
    """
    1日分のActivityをPlanItemとして組み合わせる
    それぞれのActivityのStoreは同じでなくて良い
    """

    __tablename__ = "plans"

    name: str
    description: str

    items: list["PlanItem"] = Relationship(
        back_populates="plan",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class PlanItem(Base, table=True):
    __tablename__ = "plan_activities"

    position: int
    plan_id: UUID = Field(foreign_key="plans.id")
    plan: "Plan" = Relationship(back_populates="items")
    activity_id: UUID = Field(foreign_key="activities.id")
