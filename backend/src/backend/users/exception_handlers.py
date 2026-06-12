from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request, status
from backend.users.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    PermissionDeniedError,
)


def handle_user_already_exists_error(
    request: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "User already exists"},
    )


def handle_user_not_found_error(
    request: Request, exc: UserNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "User not found"},
    )


def handle_permission_denied_error(
    request: Request, exc: PermissionDeniedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Permission denied"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserAlreadyExistsError, handle_user_already_exists_error)
    app.add_exception_handler(UserNotFoundError, handle_user_not_found_error)
    app.add_exception_handler(PermissionDeniedError, handle_permission_denied_error)
