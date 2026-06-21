from datetime import date, datetime, time

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Genre,
    Shop,
    ShopGenre,
    ShopImage,
    ShopKeyword,
    ShopMenu,
    ShopOpeningDay,
    ShopOpeningSlot,
    ShopStation,
)


class ShopRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active(self, aid: int, shop_id: int) -> Shop | None:
        stmt = select(Shop).where(
            Shop.id == shop_id,
            Shop.aid == aid,
            Shop.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def get_detail(self, aid: int, shop_id: int) -> Shop | None:
        stmt = (
            select(Shop)
            .where(Shop.id == shop_id, Shop.aid == aid, Shop.is_deleted.is_(False))
            .options(
                selectinload(Shop.genre_links).selectinload(ShopGenre.genre),
                selectinload(Shop.opening_days).selectinload(ShopOpeningDay.slots),
                selectinload(Shop.menus),
                selectinload(Shop.keywords),
                selectinload(Shop.stations),
                selectinload(Shop.images),
            )
        )
        return self.db.scalars(stmt).first()

    def search(
        self,
        aid: int,
        *,
        station: str | None = None,
        location: str | None = None,
        keyword: str | None = None,
        genre_id: int | None = None,
        q: str | None = None,
        search: str | None = None,
        open_day_of_week: int | None = None,
        open_time: time | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Shop], int]:
        base = select(Shop).where(Shop.aid == aid, Shop.is_deleted.is_(False))

        if search:
            pattern = f"%{search}%"
            sub_kw = (
                select(ShopKeyword.shop_id)
                .where(
                    ShopKeyword.aid == aid,
                    ShopKeyword.is_deleted.is_(False),
                    ShopKeyword.keyword.ilike(pattern),
                )
                .distinct()
            )
            base = base.where(or_(Shop.name.ilike(pattern), Shop.id.in_(sub_kw)))
        elif q:
            pattern = f"%{q}%"
            sub_kw = (
                select(ShopKeyword.shop_id)
                .where(
                    ShopKeyword.aid == aid,
                    ShopKeyword.is_deleted.is_(False),
                    ShopKeyword.keyword.ilike(pattern),
                )
                .distinct()
            )
            sub_st = (
                select(ShopStation.shop_id)
                .where(
                    ShopStation.aid == aid,
                    ShopStation.is_deleted.is_(False),
                    ShopStation.station_name.ilike(pattern),
                )
                .distinct()
            )
            base = base.where(
                or_(
                    Shop.name.ilike(pattern),
                    Shop.address.ilike(pattern),
                    Shop.id.in_(sub_kw),
                    Shop.id.in_(sub_st),
                )
            )
        else:
            if station:
                pattern = f"%{station}%"
                sub_st = (
                    select(ShopStation.shop_id)
                    .where(
                        ShopStation.aid == aid,
                        ShopStation.is_deleted.is_(False),
                        ShopStation.station_name.ilike(pattern),
                    )
                    .distinct()
                )
                base = base.where(Shop.id.in_(sub_st))
            if location:
                pattern = f"%{location}%"
                base = base.where(
                    or_(Shop.address.ilike(pattern), Shop.name.ilike(pattern))
                )
            if keyword:
                pattern = f"%{keyword}%"
                sub_kw = (
                    select(ShopKeyword.shop_id)
                    .where(
                        ShopKeyword.aid == aid,
                        ShopKeyword.is_deleted.is_(False),
                        ShopKeyword.keyword.ilike(pattern),
                    )
                    .distinct()
                )
                base = base.where(Shop.id.in_(sub_kw))

        if genre_id is not None:
            sub_genre = (
                select(ShopGenre.shop_id)
                .where(
                    ShopGenre.aid == aid,
                    ShopGenre.is_deleted.is_(False),
                    ShopGenre.genre_id == genre_id,
                )
                .distinct()
            )
            base = base.where(Shop.id.in_(sub_genre))

        if open_day_of_week is not None and open_time is not None:
            open_at = self._open_at_time_condition(open_time)
            sub_open = (
                select(ShopOpeningSlot.shop_id)
                .join(
                    ShopOpeningDay,
                    ShopOpeningSlot.opening_day_id == ShopOpeningDay.id,
                )
                .where(
                    ShopOpeningSlot.aid == aid,
                    ShopOpeningSlot.is_deleted.is_(False),
                    ShopOpeningDay.is_deleted.is_(False),
                    ShopOpeningDay.day_of_week == open_day_of_week,
                    open_at,
                )
                .distinct()
            )
            base = base.where(Shop.id.in_(sub_open))

        count_stmt = select(func.count()).select_from(base.subquery())
        total = int(self.db.scalar(count_stmt) or 0)

        offset = (page - 1) * per_page
        stmt = (
            base.order_by(Shop.updated_at.desc())
            .offset(offset)
            .limit(per_page)
            .options(
                selectinload(Shop.genre_links).selectinload(ShopGenre.genre),
                selectinload(Shop.stations),
            )
        )
        items = list(self.db.scalars(stmt).unique().all())
        return items, total

    @staticmethod
    def _open_at_time_condition(check_time: time):
        """指定時刻が営業時間帯内か（日跨ぎは close_time < open_time）。"""
        return or_(
            and_(
                ShopOpeningSlot.open_time <= ShopOpeningSlot.close_time,
                ShopOpeningSlot.open_time <= check_time,
                ShopOpeningSlot.close_time >= check_time,
            ),
            and_(
                ShopOpeningSlot.close_time < ShopOpeningSlot.open_time,
                or_(
                    ShopOpeningSlot.open_time <= check_time,
                    ShopOpeningSlot.close_time >= check_time,
                ),
            ),
        )

    def get_genres_by_ids(self, aid: int, genre_ids: list[int]) -> list[Genre]:
        if not genre_ids:
            return []
        stmt = select(Genre).where(
            Genre.aid == aid,
            Genre.id.in_(genre_ids),
            Genre.is_deleted.is_(False),
        )
        return list(self.db.scalars(stmt).all())

    def create_shop(
        self,
        aid: int,
        name: str,
        address: str | None,
        schedule_memo: str | None,
        last_verified_on: date | None,
        memo: str | None,
    ) -> Shop:
        shop = Shop(
            aid=aid,
            name=name,
            address=address,
            schedule_memo=schedule_memo,
            last_verified_on=last_verified_on,
            memo=memo,
        )
        self.db.add(shop)
        self.db.flush()
        return shop

    def soft_delete_shop(self, shop: Shop) -> None:
        shop.is_deleted = True
        shop.updated_at = datetime.now()
        self.db.add(shop)

    def get_image(self, aid: int, shop_id: int, image_id: int) -> ShopImage | None:
        stmt = select(ShopImage).where(
            ShopImage.id == image_id,
            ShopImage.shop_id == shop_id,
            ShopImage.aid == aid,
            ShopImage.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def replace_genres(self, shop: Shop, aid: int, genre_ids: list[int]) -> None:
        active_links = [
            link
            for link in shop.genre_links
            if not link.is_deleted
        ]
        active_map = {link.genre_id: link for link in active_links}
        desired = set(genre_ids)

        for genre_id, link in active_map.items():
            if genre_id not in desired:
                link.is_deleted = True
                link.updated_at = datetime.now()
                self.db.add(link)

        for index, genre_id in enumerate(genre_ids):
            link = active_map.get(genre_id)
            if link:
                link.sort_order = index
                link.updated_at = datetime.now()
                self.db.add(link)
            else:
                self.db.add(
                    ShopGenre(
                        shop_id=shop.id,
                        genre_id=genre_id,
                        aid=aid,
                        sort_order=index,
                    )
                )

    def replace_opening_days(
        self,
        shop: Shop,
        aid: int,
        opening_days: list[dict],
    ) -> None:
        for day in shop.opening_days:
            if not day.is_deleted:
                day.is_deleted = True
                day.updated_at = datetime.now()
                self.db.add(day)
                for slot in day.slots:
                    if not slot.is_deleted:
                        slot.is_deleted = True
                        slot.updated_at = datetime.now()
                        self.db.add(slot)

        for day_input in opening_days:
            day = ShopOpeningDay(
                shop_id=shop.id,
                aid=aid,
                day_of_week=day_input["day_of_week"],
                day_memo=day_input.get("day_memo"),
            )
            self.db.add(day)
            self.db.flush()
            for slot_input in day_input.get("slots", []):
                self.db.add(
                    ShopOpeningSlot(
                        opening_day_id=day.id,
                        shop_id=shop.id,
                        aid=aid,
                        open_time=slot_input["open_time"],
                        close_time=slot_input["close_time"],
                        sort_order=slot_input.get("sort_order", 0),
                    )
                )

    def sync_menus(self, shop: Shop, aid: int, menus: list[dict]) -> None:
        self._sync_child_items(
            shop=shop,
            aid=aid,
            existing=shop.menus,
            inputs=menus,
            factory=lambda data: ShopMenu(
                shop_id=shop.id,
                aid=aid,
                menu_name=data["menu_name"],
                memo=data.get("memo"),
                sort_order=data.get("sort_order", 0),
            ),
            updater=lambda item, data: self._update_menu(item, data),
        )

    def sync_keywords(self, shop: Shop, aid: int, keywords: list[dict]) -> None:
        self._sync_child_items(
            shop=shop,
            aid=aid,
            existing=shop.keywords,
            inputs=keywords,
            factory=lambda data: ShopKeyword(
                shop_id=shop.id,
                aid=aid,
                keyword=data["keyword"],
                sort_order=data.get("sort_order", 0),
            ),
            updater=lambda item, data: self._update_keyword(item, data),
        )

    def sync_stations(self, shop: Shop, aid: int, stations: list[dict]) -> None:
        self._sync_child_items(
            shop=shop,
            aid=aid,
            existing=shop.stations,
            inputs=stations,
            factory=lambda data: ShopStation(
                shop_id=shop.id,
                aid=aid,
                transport_type=data["transport_type"],
                line_name=data.get("line_name"),
                station_name=data["station_name"],
                walk_minutes=data.get("walk_minutes"),
                distance_memo=data.get("distance_memo"),
                sort_order=data.get("sort_order", 0),
            ),
            updater=lambda item, data: self._update_station(item, data),
        )

    def sync_images(self, shop: Shop, aid: int, images: list[dict]) -> None:
        active = {img.id: img for img in shop.images if not img.is_deleted}
        keep_ids = {data["id"] for data in images if data.get("id") is not None}

        for image_id, image in active.items():
            if image_id not in keep_ids:
                image.is_deleted = True
                image.updated_at = datetime.now()
                self.db.add(image)

        for data in images:
            image_id = data.get("id")
            if image_id is not None:
                image = active.get(image_id)
                if image is None:
                    continue
                if data.get("file_name") is not None:
                    image.file_name = data["file_name"]
                image.sort_order = data.get("sort_order", image.sort_order)
                if data.get("image_data") is not None:
                    image.image_data = data["image_data"]
                    image.file_size_bytes = len(data["image_data"])
                    image.mime_type = data["mime_type"]
                image.updated_at = datetime.now()
                self.db.add(image)
            else:
                self.db.add(
                    ShopImage(
                        shop_id=shop.id,
                        aid=aid,
                        file_name=data.get("file_name"),
                        mime_type=data["mime_type"],
                        image_data=data["image_data"],
                        file_size_bytes=len(data["image_data"]),
                        sort_order=data.get("sort_order", 0),
                    )
                )

    def _sync_child_items(
        self,
        shop: Shop,
        aid: int,
        existing: list,
        inputs: list[dict],
        factory,
        updater,
    ) -> None:
        active = {item.id: item for item in existing if not item.is_deleted}
        keep_ids = {data["id"] for data in inputs if data.get("id") is not None}

        for item_id, item in active.items():
            if item_id not in keep_ids:
                item.is_deleted = True
                item.updated_at = datetime.now()
                self.db.add(item)

        for data in inputs:
            item_id = data.get("id")
            if item_id is not None:
                item = active.get(item_id)
                if item is None:
                    continue
                updater(item, data)
            else:
                self.db.add(factory(data))

    @staticmethod
    def _update_menu(item: ShopMenu, data: dict) -> None:
        item.menu_name = data["menu_name"]
        item.memo = data.get("memo")
        item.sort_order = data.get("sort_order", item.sort_order)
        item.updated_at = datetime.now()

    @staticmethod
    def _update_keyword(item: ShopKeyword, data: dict) -> None:
        item.keyword = data["keyword"]
        item.sort_order = data.get("sort_order", item.sort_order)
        item.updated_at = datetime.now()

    @staticmethod
    def _update_station(item: ShopStation, data: dict) -> None:
        item.transport_type = data["transport_type"]
        item.line_name = data.get("line_name")
        item.station_name = data["station_name"]
        item.walk_minutes = data.get("walk_minutes")
        item.distance_memo = data.get("distance_memo")
        item.sort_order = data.get("sort_order", item.sort_order)
        item.updated_at = datetime.now()
