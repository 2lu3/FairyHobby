# auth/dependencies.py

from uuid import UUID

from fastapi import Header, Request

from backend.auth.docs_bypass import (
    get_docs_bypass_firebase_uid,
    get_docs_bypass_user_id,
)
from backend.auth.service import token_to_firebase_uid
from backend.exceptions import UnAuthorizedError


def get_firebase_uid(
    request: Request,
    authorization: str | None = Header(default=None),
) -> str:
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            return token_to_firebase_uid(token)

    bypass_firebase_uid = get_docs_bypass_firebase_uid(request)
    if bypass_firebase_uid:
        return bypass_firebase_uid

    raise UnAuthorizedError("Invalid authorization scheme")


def get_session_user_id(request: Request) -> UUID:
    user_id = request.session.get("user_id")
    if isinstance(user_id, str):
        return UUID(user_id)

    bypass_user_id = get_docs_bypass_user_id(request)
    if bypass_user_id:
        return bypass_user_id

    raise UnAuthorizedError("User not found")
