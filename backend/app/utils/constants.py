from urllib.parse import quote

MAX_IMAGE_BYTES = 5_242_880
ALLOWED_MIME_TYPES = frozenset(
    {"image/jpeg", "image/png", "image/webp", "image/gif"}
)
DELETED_GENRE_LABEL = "（削除済み）"


def build_google_maps_url(address: str | None) -> str | None:
    if not address:
        return None
    return f"https://www.google.com/maps/search/?api=1&query={quote(address)}"
