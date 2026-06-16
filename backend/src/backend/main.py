from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.auth.service import init_firebase_app
from backend.users.router import router as users_router
from backend.auth.router import router as auth_router

# from backend.activities.router import activities_router, hobbies_router
from backend.exceptions import init_exception_handlers
from backend.middlewares import init_middlewares


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase_app()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(auth_router)
# app.include_router(activities_router)


init_middlewares(app)

init_exception_handlers(app)
