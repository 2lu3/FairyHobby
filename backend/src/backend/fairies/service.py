import logging
from uuid import UUID

from sqlmodel import Session, select

from backend.exceptions import NotFoundError
from backend.fairies.models import Fairy
from backend.storage import get_bucket

logger = logging.getLogger(__name__)


def create(
    name: str,
    prompt: str,
    image_bytes: bytes,
    image_content_type: str,
    db_session: Session,
) -> Fairy:
    extension_by_content_type = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
    }
    extension = extension_by_content_type[image_content_type]

    fairy = Fairy(
        name=name,
        prompt=prompt,
        image_path="",
        image_content_type=image_content_type,
    )

    image_path = f"fairies/{fairy.id}.{extension}"
    fairy.image_path = image_path

    bucket = get_bucket()
    blob = bucket.blob(image_path)
    blob.upload_from_string(image_bytes, content_type=image_content_type)
    logger.debug("Uploaded fairy image to %s", image_path)

    db_session.add(fairy)
    db_session.commit()
    db_session.refresh(fairy)
    logger.info("Created fairy %s (name=%s)", fairy.id, fairy.name)
    return fairy


def get_all(db_session: Session) -> list[Fairy]:
    return db_session.exec(select(Fairy)).all()


def get(id: UUID, db_session: Session) -> Fairy:
    fairy = db_session.get(Fairy, id)
    if not fairy:
        raise NotFoundError()
    return fairy


def delete(id: UUID, db_session: Session):
    image_path = get(id, db_session).image_path
    fairy = get(id, db_session)
    db_session.delete(fairy)
    db_session.commit()

    blob = get_bucket().blob(image_path)
    blob.delete()
    logger.info("Deleted fairy %s (image=%s)", id, image_path)
