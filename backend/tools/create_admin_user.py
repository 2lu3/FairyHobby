"""ローカル開発用の管理者ユーザーを作成する。

通常ユーザーは Firebase 認証フロー経由でしか作成されないため、
空のローカル DB に対して activity を登録する前段として
管理者ユーザーを直接作成するためのツール。
冪等で、既に存在する場合はその ID を表示する。
"""

import logging

from sqlmodel import Session, select

from backend.activities.models import Activity, ActivityImage  # noqa: F401
from backend.activity_reviews.models import ActivityReview  # noqa: F401
from backend.database import engine
from backend.fairies.models import Fairy  # noqa: F401
from backend.plan_histories.models import PlanHistory  # noqa: F401
from backend.plans.models import Plan, PlanItem  # noqa: F401
from backend.recommendation_job.models import RecommendationJob  # noqa: F401
from backend.users.models import User
from backend.users.service import generate_icon

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ADMIN_FIREBASE_UID = "admin-local"
ADMIN_EMAIL = "admin@local.test"
ADMIN_DISPLAY_NAME = "管理者"


def main():
    with Session(engine) as db_session:
        existing = db_session.exec(
            select(User).where(User.firebase_uid == ADMIN_FIREBASE_UID)
        ).first()
        if existing:
            logger.info("Admin user already exists: %s", existing.id)
            print(existing.id)
            return

        user = User(
            firebase_uid=ADMIN_FIREBASE_UID,
            email=ADMIN_EMAIL,
            display_name=ADMIN_DISPLAY_NAME,
            icon="",
            is_admin=True,
        )
        user.icon = generate_icon(user.id)

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        logger.info("Created admin user: %s", user.id)
        print(user.id)


if __name__ == "__main__":
    main()
