from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.dependencies import get_aid
from app.schemas.shop import (
    MessageResponse,
    ShopCreateInput,
    ShopDetailResponse,
    ShopListResponse,
    ShopUpdateInput,
)
from app.services.shop_service import ShopService

router = APIRouter(prefix="/shops", tags=["shops"])


@router.get("", response_model=ShopListResponse)
def list_shops(
    station: str | None = Query(default=None),
    location: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    genre_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ShopListResponse:
    service = ShopService(db, settings)
    return service.list_shops(
        aid,
        station=station,
        location=location,
        keyword=keyword,
        genre_id=genre_id,
        q=q,
        page=page,
        per_page=per_page,
    )


@router.get("/{shop_id}", response_model=ShopDetailResponse)
def get_shop(
    shop_id: int,
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ShopDetailResponse:
    service = ShopService(db, settings)
    return ShopDetailResponse(shop=service.get_shop(aid, shop_id))


@router.post("", response_model=ShopDetailResponse, status_code=status.HTTP_201_CREATED)
def create_shop(
    payload: ShopCreateInput,
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ShopDetailResponse:
    service = ShopService(db, settings)
    return ShopDetailResponse(shop=service.create_shop(aid, payload))


@router.put("/{shop_id}", response_model=ShopDetailResponse)
def update_shop(
    shop_id: int,
    payload: ShopUpdateInput,
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ShopDetailResponse:
    service = ShopService(db, settings)
    return ShopDetailResponse(shop=service.update_shop(aid, shop_id, payload))


@router.delete("/{shop_id}", response_model=MessageResponse)
def delete_shop(
    shop_id: int,
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> MessageResponse:
    service = ShopService(db, settings)
    service.delete_shop(aid, shop_id)
    return MessageResponse(message="ok")


@router.get("/{shop_id}/images/{image_id}")
def get_shop_image(
    shop_id: int,
    image_id: int,
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    service = ShopService(db, settings)
    data, mime_type = service.get_image(aid, shop_id, image_id)
    return Response(content=data, media_type=mime_type)
