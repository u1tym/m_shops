from collections.abc import Callable

import jwt
from fastapi import HTTPException, Request, status

from app.config import get_settings


class JWTVerifier:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        cookie_name: str = "access_token",
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.cookie_name = cookie_name

    def get_raw_token(self, request: Request) -> str | None:
        return request.cookies.get(self.cookie_name)

    def decode_token(self, token: str) -> dict[str, object]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
        except jwt.PyJWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証トークンが無効です",
            ) from exc
        return payload

    def verify_request(self, request: Request) -> dict[str, object]:
        token = self.get_raw_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証が必要です",
            )
        return self.decode_token(token)

    def dependency(self) -> Callable[[Request], dict[str, object]]:
        def _require_user(request: Request) -> dict[str, object]:
            return self.verify_request(request)

        return _require_user


def create_jwt_verifier() -> JWTVerifier:
    settings = get_settings()
    return JWTVerifier(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        cookie_name=settings.cookie_name,
    )
