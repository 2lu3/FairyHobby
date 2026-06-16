from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse


class UnAuthorizedError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


def handle_unauthorized_error(request: Request, exc: UnAuthorizedError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Unauthorized"},
    )


def handle_not_found_error(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Not found"},
    )


def handle_conflict_error(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Conflict"},
    )


def handle_permission_denied_error(
    request: Request, exc: PermissionDeniedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Permission denied"},
    )


def init_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, handle_not_found_error)
    app.add_exception_handler(UnAuthorizedError, handle_unauthorized_error)
    app.add_exception_handler(ConflictError, handle_conflict_error)
    app.add_exception_handler(PermissionDeniedError, handle_permission_denied_error)
