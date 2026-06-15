from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import status
from backend.activities.exceptions import (
    HobbyAlreadyExistsError,
    HobbyNotFoundError,
    ActivityNotFoundError,
)


def handle_hobby_already_exists_error(
    request: Request, exc: HobbyAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Hobby already exists"},
    )


def handle_hobby_not_found_error(
    request: Request, exc: HobbyNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Hobby not found"},
    )


def handle_activity_not_found_error(
    request: Request, exc: ActivityNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Activity not found"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        HobbyAlreadyExistsError, handle_hobby_already_exists_error
    )
    app.add_exception_handler(HobbyNotFoundError, handle_hobby_not_found_error)
    app.add_exception_handler(ActivityNotFoundError, handle_activity_not_found_error)
