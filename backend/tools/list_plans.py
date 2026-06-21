import logging

from sqlmodel import Session, select

from backend.database import engine
from backend.plans.models import Plan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    with Session(engine) as db_session:
        plans = db_session.exec(select(Plan)).all()

        if not plans:
            logger.info("No plans found")
            return

        print(f"{'id':36}  {'name':20}  {'items':>5}  description")
        print("-" * 120)
        for plan in plans:
            print(
                f"{str(plan.id):36}  "
                f"{plan.name:20}  "
                f"{len(plan.items):>5}  "
                f"{plan.description}"
            )


if __name__ == "__main__":
    main()
