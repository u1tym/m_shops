from app.config import Settings
from app.models import Genre, Shop, ShopGenre
from app.schemas.genre import GenreOut, GenreWithCountOut
from app.schemas.shop import (
    GenreRefOut,
    ImageMetaOut,
    KeywordOut,
    MenuOut,
    OpeningDayOut,
    OpeningSlotOut,
    ShopDetailOut,
    ShopSummaryOut,
    StationOut,
    StationSummaryOut,
)
from app.utils.constants import DELETED_GENRE_LABEL, build_google_maps_url
from app.utils.time_format import format_time


class ShopSerializer:
    def __init__(self, settings: Settings) -> None:
        self._prefix = settings.api_public_prefix.rstrip("/")

    def to_summary(self, shop: Shop) -> ShopSummaryOut:
        return ShopSummaryOut(
            id=shop.id,
            name=shop.name,
            address=shop.address,
            google_maps_url=build_google_maps_url(shop.address),
            schedule_memo=shop.schedule_memo,
            last_verified_on=shop.last_verified_on,
            memo=shop.memo,
            genres=self._genres(shop),
            stations=self._station_summaries(shop),
            created_at=shop.created_at,
            updated_at=shop.updated_at,
        )

    def to_detail(self, shop: Shop) -> ShopDetailOut:
        summary = self.to_summary(shop)
        return ShopDetailOut(
            **summary.model_dump(),
            opening_days=self._opening_days(shop),
            menus=self._menus(shop),
            keywords=self._keywords(shop),
            stations=self._stations(shop),
            images=self._images(shop),
        )

    def genre_with_count(self, genre: Genre, shop_count: int | None) -> GenreWithCountOut:
        return GenreWithCountOut(
            id=genre.id,
            name=genre.name,
            sort_order=genre.sort_order,
            created_at=genre.created_at,
            updated_at=genre.updated_at,
            shop_count=shop_count,
        )

    def genre_out(self, genre: Genre) -> GenreOut:
        return GenreOut(
            id=genre.id,
            name=genre.name,
            sort_order=genre.sort_order,
            created_at=genre.created_at,
            updated_at=genre.updated_at,
        )

    def _genres(self, shop: Shop) -> list[GenreRefOut]:
        links = [link for link in shop.genre_links if not link.is_deleted]
        links.sort(key=lambda link: (link.sort_order, link.id))
        result: list[GenreRefOut] = []
        for link in links:
            genre = link.genre
            name = genre.name
            if genre.is_deleted:
                name = DELETED_GENRE_LABEL
            result.append(
                GenreRefOut(id=genre.id, name=name, sort_order=link.sort_order)
            )
        return result

    def _station_summaries(self, shop: Shop) -> list[StationSummaryOut]:
        stations = [s for s in shop.stations if not s.is_deleted]
        stations.sort(key=lambda s: (s.sort_order, s.id))
        return [
            StationSummaryOut(
                id=s.id,
                station_name=s.station_name,
                transport_type=s.transport_type,
                walk_minutes=s.walk_minutes,
                sort_order=s.sort_order,
            )
            for s in stations
        ]

    def _stations(self, shop: Shop) -> list[StationOut]:
        stations = [s for s in shop.stations if not s.is_deleted]
        stations.sort(key=lambda s: (s.sort_order, s.id))
        return [
            StationOut(
                id=s.id,
                station_name=s.station_name,
                transport_type=s.transport_type,
                walk_minutes=s.walk_minutes,
                sort_order=s.sort_order,
                line_name=s.line_name,
                distance_memo=s.distance_memo,
            )
            for s in stations
        ]

    def _opening_days(self, shop: Shop) -> list[OpeningDayOut]:
        days = [d for d in shop.opening_days if not d.is_deleted]
        days.sort(key=lambda d: d.day_of_week)
        result: list[OpeningDayOut] = []
        for day in days:
            slots = [s for s in day.slots if not s.is_deleted]
            slots.sort(key=lambda s: (s.sort_order, s.id))
            result.append(
                OpeningDayOut(
                    day_of_week=day.day_of_week,
                    day_memo=day.day_memo,
                    slots=[
                        OpeningSlotOut(
                            open_time=format_time(slot.open_time),
                            close_time=format_time(slot.close_time),
                            sort_order=slot.sort_order,
                        )
                        for slot in slots
                    ],
                )
            )
        return result

    def _menus(self, shop: Shop) -> list[MenuOut]:
        menus = [m for m in shop.menus if not m.is_deleted]
        menus.sort(key=lambda m: (m.sort_order, m.id))
        return [
            MenuOut(
                id=m.id,
                menu_name=m.menu_name,
                memo=m.memo,
                sort_order=m.sort_order,
            )
            for m in menus
        ]

    def _keywords(self, shop: Shop) -> list[KeywordOut]:
        keywords = [k for k in shop.keywords if not k.is_deleted]
        keywords.sort(key=lambda k: (k.sort_order, k.id))
        return [
            KeywordOut(id=k.id, keyword=k.keyword, sort_order=k.sort_order)
            for k in keywords
        ]

    def _images(self, shop: Shop) -> list[ImageMetaOut]:
        images = [i for i in shop.images if not i.is_deleted]
        images.sort(key=lambda i: (i.sort_order, i.id))
        return [
            ImageMetaOut(
                id=image.id,
                file_name=image.file_name,
                mime_type=image.mime_type,
                file_size_bytes=image.file_size_bytes,
                sort_order=image.sort_order,
                url=f"{self._prefix}/shops/{shop.id}/images/{image.id}",
            )
            for image in images
        ]
