import logging
import tomllib
from pathlib import Path
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import Session, select

from backend.activities.models import Activity, ActivityImage  # noqa: F401
from backend.activities.schemas import ActivityCreateRequest
from backend.activities.service import create, generate_preference_and_embeddings
from backend.activity_reviews.models import ActivityReview  # noqa: F401
from backend.database import engine
from backend.fairies.models import Fairy  # noqa: F401
from backend.plan_histories.models import PlanHistory  # noqa: F401
from backend.plans.models import Plan, PlanItem  # noqa: F401
from backend.recommendation_job.models import RecommendationJob  # noqa: F401
from backend.users.models import User  # noqa: F401
from backend.users.service import get

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ACTIVITIES_TOML_PATH = Path(__file__).parent / "example_activities.toml"


class ToolSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ADMIN_USER_ID: str


def load_activities() -> list[ActivityCreateRequest]:
    with open(ACTIVITIES_TOML_PATH, "rb") as f:
        data = tomllib.load(f)

    activities: list[ActivityCreateRequest] = []
    for raw in data.get("activities", []):
        activities.append(
            ActivityCreateRequest(
                name=raw["name"],
                description=raw["description"].strip(),
                price=raw["price"],
                duration_minutes=raw["duration_minutes"],
                image_urls=raw.get("image_urls", []),
                address=raw.get("address"),
            )
        )
    return activities


def main():
    settings = ToolSettings()

    activities = load_activities()
    if not activities:
        logger.warning("No activities found in %s", ACTIVITIES_TOML_PATH)
        return

    with Session(engine) as db_session:
        admin_user = get(settings.ADMIN_USER_ID, db_session)

        # 既存の activity を一度すべて削除してから登録し直す
        existing_activities = db_session.exec(select(Activity)).all()
        for existing in existing_activities:
            db_session.delete(existing)
        if existing_activities:
            db_session.commit()
            logger.info("Deleted %d existing activities", len(existing_activities))

        created_ids: list[UUID] = []
        for in_activity in activities:
            activity = create(in_activity, admin_user, db_session)
            created_ids.append(activity.id)
            logger.info("Created activity %s (%s)", activity.id, activity.name)

    for activity_id in created_ids:
        try:
            generate_preference_and_embeddings(activity_id)
            logger.info("Generated embeddings for activity %s", activity_id)
        except Exception:
            logger.exception(
                "Failed to generate embeddings for activity %s", activity_id
            )


if __name__ == "__main__":
    main()
