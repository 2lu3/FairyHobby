from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PlanHistoryCreateRequest(BaseModel):
    plan_id: UUID


class PlanHistoryUpdateRequest(BaseModel):
    plan_id: UUID | None = None


class PlanHistoryReadResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan_id: UUID
    created_at: datetime


class PlanHistoryDeleteResponse(BaseModel):
    id: UUID
