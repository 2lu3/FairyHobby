import logging

from sqlmodel import Session, select

from backend.database import engine
from backend.fairies.models import Fairy  # noqa: F401
from backend.recommendation_job.models import RecommendationJob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    with Session(engine) as db_session:
        jobs = db_session.exec(select(RecommendationJob)).all()

    if not jobs:
        logger.info("No recommendation jobs found")
        return

    print(
        f"{'id':36}  {'status':11}  {'date':10}  {'budget':>8}  "
        f"{'user_id':36}  {'plan_id':36}"
    )
    print("-" * 150)
    for job in jobs:
        print(
            f"{str(job.id):36}  "
            f"{job.status.value:11}  "
            f"{str(job.date):10}  "
            f"{job.budget:>8}  "
            f"{str(job.user_id):36}  "
            f"{str(job.plan_id):36}"
        )


if __name__ == "__main__":
    main()
