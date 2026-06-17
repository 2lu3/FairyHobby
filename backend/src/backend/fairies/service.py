from backend.fairies.models import Fairy
from sqlmodel import Session
from backend.storage import get_bucket


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

    db_session.add(fairy)
    db_session.commit()
    db_session.refresh(fairy)
    return fairy
