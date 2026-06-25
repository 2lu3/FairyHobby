import logging
from datetime import timedelta

import google.auth
from google.auth.transport import requests
from google.cloud import storage
from google.oauth2 import service_account

from backend.config import settings

logger = logging.getLogger(__name__)

_storage_client: storage.Client | None = None


def init_storage_client():
    global _storage_client
    if _storage_client is None:
        try:
            _storage_client = storage.Client()
        except Exception:
            logger.critical("Failed to initialize Cloud Storage client")
            raise
        logger.info("Cloud Storage client initialized")
    return _storage_client


def get_client():
    if _storage_client is None:
        raise RuntimeError("Storage client is not initialized")
    return _storage_client


def get_bucket():
    client = get_client()
    return client.bucket(settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME)


def get_presigned_url(
    file_path: str, expiration: timedelta = timedelta(hours=1)
) -> str:
    bucket = get_bucket()
    blob = bucket.blob(file_path)

    signing_kwargs: dict = {
        "version": "v4",
        "expiration": expiration,
        "method": "GET",
    }

    credentials, _ = google.auth.default()
    if not isinstance(credentials, service_account.Credentials):
        # Cloud Run 等: 秘密鍵のない Compute Engine 認証情報は IAM signBlob で署名する
        auth_request = requests.Request()
        credentials.refresh(auth_request)
        signing_kwargs["service_account_email"] = credentials.service_account_email
        signing_kwargs["access_token"] = credentials.token

    return blob.generate_signed_url(**signing_kwargs)
