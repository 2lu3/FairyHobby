# auth/dependencies.py

from uuid import UUID

from fastapi import Header, Request

from backend.auth.service import token_to_firebase_uid
from backend.exceptions import UnAuthorizedError


def get_firebase_uid(
    authorization: str | None = Header(default=None),
) -> str:
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            return token_to_firebase_uid(token)

    raise UnAuthorizedError("Invalid authorization scheme")


def get_session_user_id(request: Request) -> UUID:
    user_id = request.session.get("user_id")
    if isinstance(user_id, str):
        return UUID(user_id)

    raise UnAuthorizedError("User not found")
