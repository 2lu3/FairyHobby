from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request, status
from backend.auth.exceptions import TokenVerificationError


def handle_token_verification_error(
    request: Request, exc: TokenVerificationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Token verification error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TokenVerificationError, handle_token_verification_error)
