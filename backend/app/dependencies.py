from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.security.jwt_verifier import JWTVerifier, create_jwt_verifier


def get_aid(
    request: Request,
    settings: Settings = Depends(get_settings),
    verifier: JWTVerifier = Depends(create_jwt_verifier),
) -> int:
    if settings.debug:
        return settings.debug_aid

    claims = verifier.verify_request(request)
    sub = claims.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー ID が取得できません",
        )
    try:
        return int(str(sub))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー ID が不正です",
        ) from exc


DbSession = Session
