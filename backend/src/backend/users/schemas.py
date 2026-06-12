from uuid import UUID
from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    display_name: str

class UserUpdateRequest(BaseModel):
    display_name: str | None = None
    is_admin: bool | None = None

class UserReadResponse(BaseModel):
    """誰でも取得可能"""
    id: UUID
    display_name: str
    is_admin: bool

class UserMeReadResponse(BaseModel):
    """本人のみが取得可能"""
    id: UUID
    email: str
    display_name: str
    is_admin: bool

class UserDeleteResponse(BaseModel):
    id: UUID
