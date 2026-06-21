import logging
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import Session, select

from backend.activities.models import Activity  # noqa: F401
from backend.activity_reviews.models import ActivityReview  # noqa: F401
from backend.database import engine
from backend.stores.models import Store
from backend.stores.schemas import StoreCreateRequest
from backend.stores.service import create
from backend.users.service import get

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


STORE_NAME = "何でも屋"
STORE_DESCRIPTION = (
    "ジャンルを問わず、あらゆる趣味・体験を取り扱う何でも屋です。"
    "初心者から経験者まで楽しめる体験を幅広く提供しています。"
)


class ToolSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ADMIN_USER_ID: UUID


def main():
    settings = ToolSettings()

    with Session(engine) as db_session:
        admin_user = get(settings.ADMIN_USER_ID, db_session)

        existing_store = db_session.exec(
            select(Store).where(
                Store.name == STORE_NAME,
                Store.owner_user_id == admin_user.id,
            )
        ).first()
        if existing_store:
            logger.info("Store already exists: %s", existing_store.id)
            print(existing_store.id)
            return

        store = create(
            StoreCreateRequest(name=STORE_NAME, description=STORE_DESCRIPTION),
            admin_user,
            db_session,
        )
        logger.info("Created store: %s", store.id)
        print(store.id)


if __name__ == "__main__":
    main()
