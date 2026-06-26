from app.config import Settings
from app.models import Genre, Shop, ShopGenre
from app.schemas.genre import GenreOut, GenreWithCountOut
from app.schemas.shop import (
    GenreRefOut,
    HolidayHoursOut,
    ImageMetaOut,
    KeywordOut,
    MenuOut,
    OpeningDayOut,
    OpeningSlotOut,
    ShopDetailOut,
    ShopSummaryOut,
    StationOut,
    StationSummaryOut,
    VisitOut,
)
from app.utils.constants import DELETED_GENRE_LABEL, build_google_maps_url
from app.utils.time_format import format_time


class ShopSerializer:
    def __init__(self, settings: Settings) -> None:
        self._prefix = settings.api_public_prefix.rstrip("/")

    def to_summary(self, shop: Shop, *, include_thumbnail: bool = False) -> ShopSummaryOut:
        return ShopSummaryOut(
            id=shop.id,
            name=shop.name,
            prefecture=shop.prefecture,
            address=shop.address,
            google_maps_url=build_google_maps_url(shop.address),
            schedule_memo=shop.schedule_memo,
            last_verified_on=shop.last_verified_on,
            last_visit_on=self._last_visit_on(shop),
            memo=shop.memo,
            genres=self._genres(shop),
            stations=self._station_summaries(shop),
            thumbnail=self._thumbnail(shop) if include_thumbnail else None,
            created_at=shop.created_at,
            updated_at=shop.updated_at,
        )

    def to_detail(self, shop: Shop) -> ShopDetailOut:
        summary = self.to_summary(shop)
        return ShopDetailOut(
            **summary.model_dump(exclude={"stations"}),
            opening_days=self._opening_days(shop),
            holiday_hours=self._holiday_hours(shop),
            menus=self._menus(shop),
            keywords=self._keywords(shop),
            stations=self._stations(shop),
            visits=self._visits(shop),
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
                transport_line=s.transport_line,
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
                transport_line=s.transport_line,
                walk_minutes=s.walk_minutes,
                sort_order=s.sort_order,
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
                    is_closed=day.is_closed,
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

    def _holiday_hours(self, shop: Shop) -> HolidayHoursOut | None:
        hours_list = [h for h in shop.holiday_hours if not h.is_deleted]
        if not hours_list:
            return None
        hours = hours_list[0]
        slots = [s for s in hours.slots if not s.is_deleted]
        slots.sort(key=lambda s: (s.sort_order, s.id))
        return HolidayHoursOut(
            is_closed=hours.is_closed,
            memo=hours.memo,
            slots=[
                OpeningSlotOut(
                    open_time=format_time(slot.open_time),
                    close_time=format_time(slot.close_time),
                    sort_order=slot.sort_order,
                )
                for slot in slots
            ],
        )

    def _visits(self, shop: Shop) -> list[VisitOut]:
        visits = [v for v in shop.visits if not v.is_deleted]
        visits.sort(key=lambda v: (v.visit_date, v.id), reverse=True)
        return [
            VisitOut(id=v.id, visit_date=v.visit_date, memo=v.memo)
            for v in visits
        ]

    @staticmethod
    def _last_visit_on(shop: Shop):
        visits = [v for v in shop.visits if not v.is_deleted]
        if not visits:
            return None
        return max(v.visit_date for v in visits)

    def _thumbnail(self, shop: Shop) -> ImageMetaOut | None:
        images = [i for i in shop.images if not i.is_deleted]
        if not images:
            return None
        images.sort(key=lambda i: (i.sort_order, i.id))
        image = images[0]
        return ImageMetaOut(
            id=image.id,
            file_name=image.file_name,
            mime_type=image.mime_type,
            file_size_bytes=image.file_size_bytes,
            sort_order=image.sort_order,
            url=f"{self._prefix}/shops/{shop.id}/images/{image.id}",
        )

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
