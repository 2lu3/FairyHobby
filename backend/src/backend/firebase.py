import logging

import firebase_admin

from backend.config import settings

logger = logging.getLogger(__name__)

_firebase_app: firebase_admin.App | None = None


def init_firebase_app() -> None:
    global _firebase_app
    if _firebase_app is not None:
        return
    try:
        if settings.use_firebase_auth_emulator:
            # ローカル: Firebase Auth Emulator を利用する。
            # firebase-admin は環境変数 FIREBASE_AUTH_EMULATOR_HOST を自動参照するため、
            # 認証情報は不要。projectId のみ明示する。
            _firebase_app = firebase_admin.initialize_app(
                options={"projectId": settings.GOOGLE_CLOUD_PROJECT_ID}
            )
        else:
            _firebase_app = firebase_admin.initialize_app()
    except Exception:
        logger.critical("Failed to initialize Firebase app")
        raise
    logger.info("Firebase app initialized")


def get_app() -> firebase_admin.App:
    if _firebase_app is None:
        raise RuntimeError("Firebase app is not initialized")
    return _firebase_app
