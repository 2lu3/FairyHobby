import logging

from sqlmodel import Session, select

from backend.database import engine

# 全モデルをレジストリに登録し、相互参照のリレーションを解決できるようにする
import backend.users.models  # noqa: F401
import backend.activities.models  # noqa: F401
import backend.activity_reviews.models  # noqa: F401
import backend.plans.models  # noqa: F401
import backend.recommendation_job.models  # noqa: F401
from backend.fairies.models import Fairy
from backend.fairies.service import generate_embeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    with Session(engine) as db_session:
        fairies = db_session.exec(select(Fairy)).all()
        target_ids = [fairy.id for fairy in fairies if not fairy.embeddings]

    if not target_ids:
        logger.info("All fairies already have embeddings")
        return

    logger.info("Backfilling embeddings for %d fairies", len(target_ids))
    for fairy_id in target_ids:
        generate_embeddings(fairy_id)
        logger.info("Generated embeddings for fairy: %s", fairy_id)


if __name__ == "__main__":
    main()
