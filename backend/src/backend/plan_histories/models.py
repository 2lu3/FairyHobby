from uuid import UUID

from sqlmodel import Field

from backend.database import Base


class PlanHistory(Base, table=True):
    """ユーザーが体験した（選んだ）Planの履歴。

    この履歴を辿ることで、過去のPlan一覧とそれに紐づくActivity一覧を取得し、
    ActivityReviewの投稿につなげる。
    """

    __tablename__ = "plan_histories"

    user_id: UUID = Field(foreign_key="users.id")
    plan_id: UUID = Field(foreign_key="plans.id")
