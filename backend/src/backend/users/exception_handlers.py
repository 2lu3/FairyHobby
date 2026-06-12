from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request, status
from backend.users.exceptions import UserAlreadyExistsError, UserNotFoundError

def handle_user_already_exists_error(request: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "User already exists"},
    )

def handle_user_not_found_error(request: Request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "User not found"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserAlreadyExistsError, handle_user_already_exists_error)
    app.add_exception_handler(UserNotFoundError, handle_user_not_found_error)