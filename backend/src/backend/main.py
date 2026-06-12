from fastapi import FastAPI
from backend.users.router import router as users_router
from backend.auth.exception_handlers import register_exception_handlers
from backend.users.exception_handlers import register_exception_handlers

app = FastAPI()

app.include_router(users_router)
register_exception_handlers(app)
register_exception_handlers(app)