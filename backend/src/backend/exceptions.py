import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class UnAuthorizedError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


def handle_unauthorized_error(request: Request, exc: UnAuthorizedError) -> JSONResponse:
    logger.warning(
        "Unauthorized: %s %s (%s)",
        request.method,
        request.url.path,
        str(exc) or "-",
    )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Unauthorized"},
    )


def handle_not_found_error(request: Request, exc: NotFoundError) -> JSONResponse:
    logger.warning(
        "Not found: %s %s (%s)",
        request.method,
        request.url.path,
        str(exc) or "-",
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Not found"},
    )


def handle_conflict_error(request: Request, exc: ConflictError) -> JSONResponse:
    logger.warning(
        "Conflict: %s %s (%s)",
        request.method,
        request.url.path,
        str(exc) or "-",
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Conflict"},
    )


def handle_permission_denied_error(
    request: Request, exc: PermissionDeniedError
) -> JSONResponse:
    logger.warning(
        "Permission denied: %s %s (%s)",
        request.method,
        request.url.path,
        str(exc) or "-",
    )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Permission denied"},
    )


def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception: %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def init_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, handle_not_found_error)
    app.add_exception_handler(UnAuthorizedError, handle_unauthorized_error)
    app.add_exception_handler(ConflictError, handle_conflict_error)
    app.add_exception_handler(PermissionDeniedError, handle_permission_denied_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
