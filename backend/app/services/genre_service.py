from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.repositories.genre_repository import GenreRepository
from app.schemas.genre import GenreCreateInput, GenreOut, GenreUpdateInput
from app.services.serializer import ShopSerializer


class GenreService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.repo = GenreRepository(db)
        self.serializer = ShopSerializer(settings)

    def list_genres(self, aid: int, include_usage_count: bool) -> list:
        genres = self.repo.list_active(aid)
        if not include_usage_count:
            return [self.serializer.genre_with_count(g, None) for g in genres]
        return [
            self.serializer.genre_with_count(
                genre,
                self.repo.count_shop_usage(aid, genre.id),
            )
            for genre in genres
        ]

    def create_genre(self, aid: int, payload: GenreCreateInput) -> GenreOut:
        if self.repo.find_by_name_active(aid, payload.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="同名のジャンルが既に存在します",
            )
        genre = self.repo.create(aid, payload.name, payload.sort_order)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="同名のジャンルが既に存在します",
            ) from exc
        self.db.refresh(genre)
        return self.serializer.genre_out(genre)

    def update_genre(
        self,
        aid: int,
        genre_id: int,
        payload: GenreUpdateInput,
    ) -> GenreOut:
        genre = self.repo.get_active(aid, genre_id)
        if genre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ジャンルが見つかりません",
            )
        if payload.name is not None:
            existing = self.repo.find_by_name_active(aid, payload.name)
            if existing is not None and existing.id != genre.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="同名のジャンルが既に存在します",
                )
            genre.name = payload.name
        if payload.sort_order is not None:
            genre.sort_order = payload.sort_order
        genre.updated_at = datetime.now()
        self.db.add(genre)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="同名のジャンルが既に存在します",
            ) from exc
        self.db.refresh(genre)
        return self.serializer.genre_out(genre)

    def delete_genre(self, aid: int, genre_id: int) -> None:
        genre = self.repo.get_active(aid, genre_id)
        if genre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ジャンルが見つかりません",
            )
        self.repo.soft_delete(genre)
        self.db.commit()
