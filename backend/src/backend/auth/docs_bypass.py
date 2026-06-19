from uuid import UUID

from fastapi import Request

from backend.config import settings

DOCS_REFERER_PATHS = ("/docs", "/redoc")


def is_docs_request(request: Request) -> bool:
    """dev 環境で Swagger / ReDoc からのリクエストかどうかを判定する。"""
    if settings.APP_ENV != "dev":
        return False

    referer = request.headers.get("referer", "")
    if any(path in referer for path in DOCS_REFERER_PATHS):
        return True

    return request.headers.get("x-docs-bypass", "").lower() in ("1", "true", "yes")


def get_docs_bypass_user_id(request: Request) -> UUID | None:
    if not is_docs_request(request):
        return None

    header = request.headers.get("x-docs-user-id")
    if header:
        try:
            return UUID(header)
        except ValueError:
            return None

    return settings.DOCS_BYPASS_USER_ID


def get_docs_bypass_firebase_uid(request: Request) -> str | None:
    if not is_docs_request(request):
        return None

    header = request.headers.get("x-docs-firebase-uid")
    if header:
        return header

    return settings.DOCS_BYPASS_FIREBASE_UID
