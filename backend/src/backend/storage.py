import logging
import time
from datetime import timedelta
from urllib.parse import quote

import google.auth
from google.auth.credentials import AnonymousCredentials
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
            if settings.use_storage_emulator:
                # ローカル: fake-gcs-server に匿名認証で接続する
                _storage_client = storage.Client(
                    project=settings.GOOGLE_CLOUD_PROJECT_ID,
                    credentials=AnonymousCredentials(),
                )
                _ensure_bucket(_storage_client)
            else:
                _storage_client = storage.Client()
        except Exception:
            logger.critical("Failed to initialize Cloud Storage client")
            raise
        logger.info("Cloud Storage client initialized")
    return _storage_client


def _ensure_bucket(client: storage.Client, retries: int = 30) -> None:
    """エミュレータ上にバケットが無ければ作成する。

    コンテナ起動直後は fake-gcs-server がまだ応答しないことがあるため、
    接続できるまで数回リトライする。
    """
    bucket_name = settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            bucket = client.bucket(bucket_name)
            if not bucket.exists():
                client.create_bucket(bucket)
                logger.info("Created bucket %s on storage emulator", bucket_name)
            return
        except Exception as e:  # noqa: BLE001 - エミュレータ起動待ちのため握りつぶす
            last_error = e
            logger.info(
                "Waiting for storage emulator (attempt %d/%d)", attempt + 1, retries
            )
            time.sleep(1)
    raise RuntimeError("Storage emulator is not reachable") from last_error


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
    if settings.use_storage_emulator:
        # ローカル: fake-gcs-server は署名なしでオブジェクトを配信できるため、
        # ブラウザから到達可能な公開ダウンロードURLをそのまま返す。
        base = (settings.GCS_PUBLIC_ENDPOINT or settings.STORAGE_EMULATOR_HOST).rstrip(
            "/"
        )
        bucket_name = settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME
        encoded_path = quote(file_path, safe="")
        return f"{base}/storage/v1/b/{bucket_name}/o/{encoded_path}?alt=media"

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
