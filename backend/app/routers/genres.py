from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.dependencies import get_aid
from app.schemas.genre import (
    GenreCreateInput,
    GenreListResponse,
    GenreResponse,
    GenreUpdateInput,
)
from app.schemas.shop import MessageResponse
from app.services.genre_service import GenreService

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("", response_model=GenreListResponse)
def list_genres(
    include_usage_count: bool = Query(default=False),
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> GenreListResponse:
    service = GenreService(db, settings)
    return GenreListResponse(items=service.list_genres(aid, include_usage_count))


@router.post("", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
def create_genre(
    payload: GenreCreateInput,
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> GenreResponse:
    service = GenreService(db, settings)
    return GenreResponse(genre=service.create_genre(aid, payload))


@router.patch("/{genre_id}", response_model=GenreResponse)
def update_genre(
    genre_id: int,
    payload: GenreUpdateInput,
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> GenreResponse:
    service = GenreService(db, settings)
    return GenreResponse(genre=service.update_genre(aid, genre_id, payload))


@router.delete("/{genre_id}", response_model=MessageResponse)
def delete_genre(
    genre_id: int,
    aid: int = Depends(get_aid),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> MessageResponse:
    service = GenreService(db, settings)
    service.delete_genre(aid, genre_id)
    return MessageResponse(message="ok")
