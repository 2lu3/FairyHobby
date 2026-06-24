import logging
from uuid import UUID

from sqlmodel import Session, select

from backend.activities.models import Activity, ActivityImage
from backend.activities.schemas import ActivityCreateRequest, ActivityUpdateRequest
from backend.exceptions import NotFoundError, PermissionDeniedError
from backend.users.models import User
from openai import OpenAI
from backend.config import settings
from backend.database import engine

logger = logging.getLogger(__name__)


def create(
    in_activity: ActivityCreateRequest, current_user: User, db_session: Session
) -> Activity:
    activity = Activity(
        name=in_activity.name,
        description=in_activity.description,
        price=in_activity.price,
        duration_minutes=in_activity.duration_minutes,
        owner_user_id=current_user.id,
        address=in_activity.address,
        preference_text=None,
    )

    for image_url in in_activity.image_urls:
        activity_image = ActivityImage(image_url=image_url)
        activity.images.append(activity_image)

    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    logger.info("Created activity %s by %s", activity.id, current_user.id)
    return activity


def get(activity_id: UUID, db_session: Session) -> Activity:
    activity = db_session.get(Activity, activity_id)
    if not activity:
        raise NotFoundError()
    return activity


def list_by_owner(owner_user_id: UUID, db_session: Session) -> list[Activity]:
    return list(
        db_session.exec(
            select(Activity).where(Activity.owner_user_id == owner_user_id)
        ).all()
    )


def update(
    activity_id: UUID,
    in_activity: ActivityUpdateRequest,
    current_user: User,
    db_session: Session,
) -> Activity:
    activity = db_session.get(Activity, activity_id)
    if not activity:
        raise NotFoundError()

    if activity.owner_user_id != current_user.id:
        raise PermissionDeniedError()

    if in_activity.name is not None:
        activity.name = in_activity.name
    if in_activity.description is not None:
        activity.description = in_activity.description
    if in_activity.price is not None:
        activity.price = in_activity.price
    if in_activity.duration_minutes is not None:
        activity.duration_minutes = in_activity.duration_minutes
    if in_activity.image_urls is not None:
        activity.images.clear()
        for image_url in in_activity.image_urls:
            activity.images.append(ActivityImage(image_url=image_url))
    if in_activity.address is not None:
        activity.address = in_activity.address

    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    logger.info("Updated activity %s by %s", activity.id, current_user.id)
    return activity


def delete(activity_id: UUID, current_user: User, db_session: Session) -> Activity:
    activity = db_session.get(Activity, activity_id)
    if not activity:
        raise NotFoundError()

    if activity.owner_user_id != current_user.id:
        raise PermissionDeniedError()

    db_session.delete(activity)
    db_session.commit()
    logger.info("Deleted activity %s by %s", activity_id, current_user.id)
    return activity


def generate_preference_and_embeddings(activity_id: UUID) -> None:
    with Session(engine) as db_session:
        activity = db_session.get(Activity, activity_id)
        if activity is None:
            logger.warning(
                "Activity %s not found for preference and embedding generation",
                activity_id,
            )
            return

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "以下の体験情報から、推薦検索用の嗜好プロファイルを作成してください。「どんな雰囲気か」「どんな人に向いているか」「どんな人には向きにくいか」「必要なエネルギー感」「社交性」「創造性」「雰囲気」",
                },
                {
                    "role": "user",
                    "content": f"体験名: {activity.name}\n説明:{activity.description}\nレビュー: {'\n'.join([review.text for review in activity.reviews])}",
                },
            ],
        )

        preference_text = response.choices[0].message.content
        embedding_response = client.embeddings.create(
            input=preference_text,
            model="text-embedding-3-small",
        )
        embeddings = embedding_response.data[0].embedding

        activity.preference_text = preference_text
        activity.embeddings = embeddings
        db_session.add(activity)
        db_session.commit()
