from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Genre, ShopGenre


class GenreRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self, aid: int) -> list[Genre]:
        stmt = (
            select(Genre)
            .where(Genre.aid == aid, Genre.is_deleted.is_(False))
            .order_by(Genre.sort_order, Genre.name)
        )
        return list(self.db.scalars(stmt).all())

    def get_active(self, aid: int, genre_id: int) -> Genre | None:
        stmt = select(Genre).where(
            Genre.id == genre_id,
            Genre.aid == aid,
            Genre.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def get_by_id(self, aid: int, genre_id: int) -> Genre | None:
        stmt = select(Genre).where(Genre.id == genre_id, Genre.aid == aid)
        return self.db.scalars(stmt).first()

    def find_by_name_active(self, aid: int, name: str) -> Genre | None:
        stmt = select(Genre).where(
            Genre.aid == aid,
            Genre.name == name,
            Genre.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def count_shop_usage(self, aid: int, genre_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(ShopGenre)
            .where(
                ShopGenre.aid == aid,
                ShopGenre.genre_id == genre_id,
                ShopGenre.is_deleted.is_(False),
            )
        )
        return int(self.db.scalar(stmt) or 0)

    def create(self, aid: int, name: str, sort_order: int) -> Genre:
        genre = Genre(aid=aid, name=name, sort_order=sort_order)
        self.db.add(genre)
        self.db.flush()
        return genre

    def soft_delete(self, genre: Genre) -> None:
        genre.is_deleted = True
        genre.updated_at = datetime.now()
        self.db.add(genre)
