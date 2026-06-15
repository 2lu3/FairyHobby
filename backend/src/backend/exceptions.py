from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status


class UnAuthorizedError(Exception):
    pass


def handle_unauthorized_error(request: Request, exc: UnAuthorizedError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Unauthorized"},
    )


class NotFoundError(Exception):
    pass


def handle_not_found_error(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Not found"},
    )


class ConflictError(Exception):
    pass


def handle_conflict_error(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Conflict"},
    )


class PermissionDeniedError(Exception):
    pass


def handle_permission_denied_error(
    request: Request, exc: PermissionDeniedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Permission denied"},
    )
