import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.activities.router import router as activities_router
from backend.auth.router import router as auth_router
from backend.config import settings
from backend.exceptions import init_exception_handlers
from backend.fairies.router import router as fairies_router
from backend.firebase import init_firebase_app
from backend.logging import setup_logging
from backend.middlewares import init_middlewares
from backend.plans.router import router as plans_router
from backend.storage import init_storage_client
from backend.stores.router import router as stores_router
from backend.users.router import router as users_router

logger = logging.getLogger(__name__)

DOCS_DESCRIPTION = """
### Swagger からの API 試行（dev のみ）

`/docs` または `/redoc` から呼び出した場合、セッションと Firebase 認証をバイパスできます。

- 既定ユーザー: `.env` の `DOCS_BYPASS_USER_ID` / `DOCS_BYPASS_FIREBASE_UID`
- リクエストごとに上書き: `X-Docs-User-Id` / `X-Docs-Firebase-Uid`
- Referer が付かない場合の代替: `X-Docs-Bypass: true`
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting application")
    init_firebase_app()
    init_storage_client()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    lifespan=lifespan,
    description=DOCS_DESCRIPTION if settings.APP_ENV == "dev" else None,
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(stores_router)
app.include_router(activities_router)
app.include_router(plans_router)
app.include_router(fairies_router)

init_middlewares(app)
init_exception_handlers(app)
