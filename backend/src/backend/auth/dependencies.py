# auth/dependencies.py

from fastapi import Header, Request
from uuid import UUID
from backend.auth.service import token_to_firebase_uid
from backend.exceptions import UnAuthorizedError


def get_firebase_uid(
    authorization: str = Header(),
) -> str:
    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise UnAuthorizedError("Invalid authorization scheme")

    return token_to_firebase_uid(token)


def get_session_user_id(request: Request):
    user_id = request.session.get("user_id")
    if not isinstance(user_id, str):
        raise UnAuthorizedError("User not found")
    return UUID(user_id)
