from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.auth.service import init_firebase_app
from backend.users.router import router as users_router

# from backend.activities.router import activities_router, hobbies_router
from backend.exceptions import (
    NotFoundError,
    ConflictError,
    PermissionDeniedError,
    handle_not_found_error,
    handle_conflict_error,
    handle_permission_denied_error,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase_app()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
# app.include_router(activities_router)


app.add_exception_handler(NotFoundError, handle_not_found_error)
app.add_exception_handler(ConflictError, handle_conflict_error)
app.add_exception_handler(PermissionDeniedError, handle_permission_denied_error)
