import firebase_admin
from firebase_admin import auth
from firebase_admin.auth import (
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
    UserDisabledError,
    UserNotFoundError,
)
from firebase_admin.exceptions import FirebaseError
from backend.auth.exceptions import TokenVerificationError

_firebase_app: firebase_admin.App | None = None


def init_firebase_app() -> None:
    """Firebase アプリを初期化する"""
    global _firebase_app
    if _firebase_app is not None:
        return
    _firebase_app = firebase_admin.initialize_app()


def token_to_firebase_uid(token: str) -> str:
    """firebase id tokenを検証し、firebase uidを返す

    Args:
        token (str): クライアントに渡されたfirebase id token

    Raises:
        TokenVerificationError:

    Returns:
        str: デコードされたtoken
    """
    try:
        return firebase_admin.auth.verify_id_token(token).get("uid")
    except (
        ValueError,
        InvalidIdTokenError,
        ExpiredIdTokenError,
        RevokedIdTokenError,
        UserDisabledError,
    ) as e:
        raise TokenVerificationError("Failed to verify firebase id token") from e


def get_email_from_firebase(firebase_uid: str) -> str:
    """firebase経由で登録したgoogleアカウントのメールアドレスを取得する

    Args:
        firebase_uid (str): firebase uid

    Raises:
        TokenVerificationError:

    Returns:
        str: email address
    """
    try:
        user = auth.get_user(firebase_uid)
        return user.email
    except (ValueError, UserNotFoundError, FirebaseError) as e:
        raise TokenVerificationError("Failed to get email from firebase") from e


def firebase_app() -> firebase_admin.App:
    """Firebase アプリを取得する"""
    global _firebase_app
    if _firebase_app is None:
        raise RuntimeError("Firebase app is not initialized")
    return _firebase_app
