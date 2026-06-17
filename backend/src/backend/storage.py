from google.cloud import storage
from backend.config import settings

_storage_client: storage.Client | None = None


def init_storage_client():
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client


def get_client():
    if _storage_client is None:
        raise RuntimeError("Storage client is not initialized")
    return _storage_client


def get_bucket():
    client = get_client()
    return client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME)


def get_public_url(file_path: str) -> str:
    bucket = get_bucket()
    blob = bucket.blob(file_path)
    return blob.public_url
