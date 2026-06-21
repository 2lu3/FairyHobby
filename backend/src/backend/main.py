import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.activities.router import router as activities_router
from backend.activity_reviews.router import router as activity_reviews_router
from backend.auth.router import router as auth_router
from backend.exceptions import init_exception_handlers
from backend.fairies.router import router as fairies_router
from backend.firebase import init_firebase_app
from backend.logging import setup_logging
from backend.middlewares import init_middlewares
from backend.plan_histories.router import router as plan_histories_router
from backend.plans.router import router as plans_router
from backend.recommendation_job.router import router as recommendation_router
from backend.storage import init_storage_client
from backend.stores.router import router as stores_router
from backend.users.router import router as users_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting application")
    init_firebase_app()
    init_storage_client()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(stores_router)
app.include_router(activities_router)
app.include_router(activity_reviews_router)
app.include_router(plans_router)
app.include_router(plan_histories_router)
app.include_router(fairies_router)
app.include_router(recommendation_router)

init_middlewares(app)
init_exception_handlers(app)
