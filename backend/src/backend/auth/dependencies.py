# auth/dependencies.py

from fastapi import Depends
from fastapi.security import HTTPBearer

from backend.auth.service import token_to_firebase_uid

security = HTTPBearer()

def get_firebase_uid(
    credentials=Depends(security),
) -> str:
    """ firebase id tokenを検証し、firebase uidを返す
    Raises:
        TokenVerificationError: 
    """
    return token_to_firebase_uid(credentials.credentials)