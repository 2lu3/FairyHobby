from fastapi import FastAPI
from backend.users.router import router as users_router
from backend.auth.exception_handlers import auth_register_exception_handlers
from backend.users.exception_handlers import users_register_exception_handlers

app = FastAPI()

app.include_router(users_router)
auth_register_exception_handlers(app)
users_register_exception_handlers(app)
