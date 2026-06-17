from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.firebase import init_firebase_app
from backend.users.router import router as users_router
from backend.auth.router import router as auth_router
from backend.stores.router import router as stores_router
from backend.activities.router import router as activities_router
from backend.plans.router import router as plans_router
from backend.fairies.router import router as fairies_router
from backend.exceptions import init_exception_handlers
from backend.middlewares import init_middlewares
from backend.storage import init_storage_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase_app()
    init_storage_client()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(stores_router)
app.include_router(activities_router)
app.include_router(plans_router)
app.include_router(fairies_router)

init_middlewares(app)
init_exception_handlers(app)
