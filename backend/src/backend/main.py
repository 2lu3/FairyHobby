from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.auth.service import init_firebase_app
from backend.users.router import router as users_router
from backend.auth.exception_handlers import (
    register_exception_handlers as auth_register_exception_handlers,
)
from backend.users.exception_handlers import (
    register_exception_handlers as users_register_exception_handlers,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase_app()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)

auth_register_exception_handlers(app)
users_register_exception_handlers(app)
