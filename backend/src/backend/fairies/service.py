import logging
from openai import OpenAI
from uuid import UUID

from sqlmodel import Session, select

from backend.exceptions import NotFoundError
from backend.fairies.models import Fairy
from backend.fairies.schemas import FairyUpdateRequest
from backend.storage import get_bucket
from backend.config import settings
from backend.database import engine

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


def update(id: UUID, in_fairy: FairyUpdateRequest, db_session: Session) -> Fairy:
    fairy = get(id, db_session)
    if in_fairy.name is not None:
        fairy.name = in_fairy.name
    if in_fairy.prompt is not None:
        fairy.prompt = in_fairy.prompt
    db_session.add(fairy)
    db_session.commit()
    db_session.refresh(fairy)
    return fairy


def delete(id: UUID, db_session: Session):
    image_path = get(id, db_session).image_path
    fairy = get(id, db_session)
    db_session.delete(fairy)
    db_session.commit()

    blob = get_bucket().blob(image_path)
    blob.delete()
    logger.info("Deleted fairy %s (image=%s)", id, image_path)


def generate_embeddings(fairy_id: UUID) -> None:
    with Session(engine) as db_session:
        fairy = db_session.get(Fairy, fairy_id)
        if fairy is None:
            logger.warning("Fairy %s not found for embedding generation", fairy_id)
            return

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            input=fairy.prompt,
            model="text-embedding-3-small",
        )
        fairy.embeddings = response.data[0].embedding
        db_session.add(fairy)
        db_session.commit()
