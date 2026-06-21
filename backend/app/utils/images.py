import base64
import re

from fastapi import HTTPException, status

from app.utils.constants import ALLOWED_MIME_TYPES, MAX_IMAGE_BYTES

_DATA_URL_PATTERN = re.compile(r"^data:[^;]+;base64,(.+)$", re.DOTALL)


def decode_image_base64(data_base64: str) -> bytes:
    raw = data_base64.strip()
    match = _DATA_URL_PATTERN.match(raw)
    if match:
        raw = match.group(1)
    try:
        data = base64.b64decode(raw, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="画像データの Base64 形式が不正です",
        ) from exc
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="画像データが空です",
        )
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="画像サイズが 5MB を超えています",
        )
    return data


def validate_mime_type(mime_type: str) -> str:
    normalized = mime_type.strip().lower()
    if normalized not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"許可されていない画像形式です: {mime_type}",
        )
    return normalized
