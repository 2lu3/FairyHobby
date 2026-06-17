import firebase_admin

_firebase_app: firebase_admin.App | None = None


def init_firebase_app() -> None:
    global _firebase_app
    if _firebase_app is not None:
        return
    _firebase_app = firebase_admin.initialize_app()


def get_app() -> firebase_admin.App:
    if _firebase_app is None:
        raise RuntimeError("Firebase app is not initialized")
    return _firebase_app
