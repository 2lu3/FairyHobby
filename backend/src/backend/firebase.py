import logging

import firebase_admin

logger = logging.getLogger(__name__)

_firebase_app: firebase_admin.App | None = None


def init_firebase_app() -> None:
    global _firebase_app
    if _firebase_app is not None:
        return
    try:
        _firebase_app = firebase_admin.initialize_app()
    except Exception:
        logger.critical("Failed to initialize Firebase app")
        raise
    logger.info("Firebase app initialized")


def get_app() -> firebase_admin.App:
    if _firebase_app is None:
        raise RuntimeError("Firebase app is not initialized")
    return _firebase_app
