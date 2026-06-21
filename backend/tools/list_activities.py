import logging

from sqlmodel import Session, select

from backend.activities.models import Activity
from backend.activity_reviews.models import ActivityReview  # noqa: F401
from backend.database import engine
from backend.users.models import User  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    with Session(engine) as db_session:
        activities = db_session.exec(select(Activity)).all()

    if not activities:
        logger.info("No activities found")
        return

    print(
        f"{'id':36}  {'name':20}  {'price':>8}  {'duration':>8}  {'owner_store_id':36}"
    )
    print("-" * 120)
    for activity in activities:
        print(
            f"{str(activity.id):36}  "
            f"{activity.name:20}  "
            f"{activity.price:>8}  "
            f"{activity.duration_minutes:>8}  "
            f"{str(activity.owner_store_id):36}"
        )


if __name__ == "__main__":
    main()
