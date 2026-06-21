import logging

from sqlmodel import Session

from backend.activities.models import Activity  # noqa: F401
from backend.activity_reviews.models import ActivityReview  # noqa: F401
from backend.database import engine
from backend.users.service import get_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    with Session(engine) as db_session:
        users = get_all(db_session)

    if not users:
        logger.info("No users found")
        return

    print(f"{'id':36}  {'is_admin':8}  {'display_name':20}  email")
    print("-" * 90)
    for user in users:
        print(
            f"{str(user.id):36}  "
            f"{str(user.is_admin):8}  "
            f"{user.display_name:20}  "
            f"{user.email}"
        )


if __name__ == "__main__":
    main()
