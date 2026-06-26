from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.repositories.shop_repository import ShopRepository
from app.schemas.shop import (
    ShopCreateInput,
    ShopDetailOut,
    ShopListResponse,
    ShopSummaryOut,
    ShopUpdateInput,
)
from app.services.serializer import ShopSerializer
from app.utils.images import decode_image_base64, validate_mime_type
from app.utils.prefectures import PREFECTURE_SET, normalize_prefecture


class ShopService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.repo = ShopRepository(db)
        self.serializer = ShopSerializer(settings)

    def list_shops(
        self,
        aid: int,
        *,
        station: str | None,
        location: str | None,
        keyword: str | None,
        genre_id: int | None,
        q: str | None,
        search: str | None,
        open_day_of_week: int | None,
        open_time: str | None,
        prefecture: str | None,
        has_image: bool | None,
        page: int,
        per_page: int,
    ) -> ShopListResponse:
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        parsed_open_time: time | None = None
        if open_time is not None:
            try:
                hour, minute = open_time.split(":", 1)
                parsed_open_time = time(int(hour), int(minute))
            except (ValueError, AttributeError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="営業時刻の形式が不正です",
                ) from exc
        if (open_day_of_week is None) != (parsed_open_time is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="営業時刻の検索には曜日と時刻の両方が必要です",
            )
        normalized_prefecture = normalize_prefecture(prefecture)
        if normalized_prefecture is not None and normalized_prefecture not in PREFECTURE_SET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="都道府県が不正です",
            )
        shops, total = self.repo.search(
            aid,
            station=station,
            location=location,
            keyword=keyword,
            genre_id=genre_id,
            q=q,
            search=search,
            open_day_of_week=open_day_of_week,
            open_time=parsed_open_time,
            prefecture=normalized_prefecture,
            has_image=has_image,
            page=page,
            per_page=per_page,
        )
        return ShopListResponse(
            items=[
                self.serializer.to_summary(
                    shop, include_thumbnail=has_image is True
                )
                for shop in shops
            ],
            total=total,
            page=page,
            per_page=per_page,
        )

    def get_shop(self, aid: int, shop_id: int) -> ShopDetailOut:
        shop = self.repo.get_detail(aid, shop_id)
        if shop is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="店舗が見つかりません",
            )
        return self.serializer.to_detail(shop)

    def create_shop(self, aid: int, payload: ShopCreateInput) -> ShopDetailOut:
        self._validate_genre_ids(aid, payload.genre_ids)
        self._validate_unique_keywords(payload.keywords)

        shop = self.repo.create_shop(
            aid=aid,
            name=payload.name,
            prefecture=payload.prefecture,
            address=payload.address,
            schedule_memo=payload.schedule_memo,
            last_verified_on=payload.last_verified_on,
            memo=payload.memo,
        )
        self._apply_children(shop, aid, payload)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="データの整合性エラーが発生しました",
            ) from exc
        detail = self.repo.get_detail(aid, shop.id)
        assert detail is not None
        return self.serializer.to_detail(detail)

    def update_shop(
        self,
        aid: int,
        shop_id: int,
        payload: ShopUpdateInput,
    ) -> ShopDetailOut:
        shop = self.repo.get_detail(aid, shop_id)
        if shop is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="店舗が見つかりません",
            )

        self._validate_genre_ids(aid, payload.genre_ids)
        self._validate_unique_keywords(payload.keywords)

        shop.name = payload.name
        shop.prefecture = payload.prefecture
        shop.address = payload.address
        shop.schedule_memo = payload.schedule_memo
        shop.last_verified_on = payload.last_verified_on
        shop.memo = payload.memo
        shop.updated_at = datetime.now()
        self.db.add(shop)

        self._apply_children(shop, aid, payload)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="データの整合性エラーが発生しました",
            ) from exc
        detail = self.repo.get_detail(aid, shop.id)
        assert detail is not None
        return self.serializer.to_detail(detail)

    def delete_shop(self, aid: int, shop_id: int) -> None:
        shop = self.repo.get_active(aid, shop_id)
        if shop is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="店舗が見つかりません",
            )
        self.repo.soft_delete_shop(shop)
        self.db.commit()

    def get_image(self, aid: int, shop_id: int, image_id: int) -> tuple[bytes, str]:
        shop = self.repo.get_active(aid, shop_id)
        if shop is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="店舗が見つかりません",
            )
        image = self.repo.get_image(aid, shop_id, image_id)
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="画像が見つかりません",
            )
        return image.image_data, image.mime_type

    def _validate_genre_ids(self, aid: int, genre_ids: list[int]) -> None:
        if not genre_ids:
            return
        found = self.repo.get_genres_by_ids(aid, genre_ids)
        if len(found) != len(set(genre_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定されたジャンルが見つかりません",
            )

    @staticmethod
    def _validate_unique_keywords(keywords) -> None:
        seen: set[str] = set()
        for item in keywords:
            key = item.keyword.strip()
            if key in seen:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="キーワードが重複しています",
                )
            seen.add(key)

    def _apply_children(self, shop, aid: int, payload) -> None:
        self.repo.replace_genres(shop, aid, payload.genre_ids)
        self.repo.replace_opening_days(
            shop,
            aid,
            [
                {
                    "day_of_week": day.day_of_week,
                    "day_memo": day.day_memo,
                    "is_closed": day.is_closed,
                    "slots": [
                        {
                            "open_time": slot.open_time,
                            "close_time": slot.close_time,
                            "sort_order": slot.sort_order,
                        }
                        for slot in day.slots
                    ],
                }
                for day in payload.opening_days
            ],
        )
        holiday = payload.holiday_hours
        self.repo.replace_holiday_hours(
            shop,
            aid,
            None
            if holiday is None
            else {
                "is_closed": holiday.is_closed,
                "memo": holiday.memo,
                "slots": [
                    {
                        "open_time": slot.open_time,
                        "close_time": slot.close_time,
                        "sort_order": slot.sort_order,
                    }
                    for slot in holiday.slots
                ],
            },
        )
        self.repo.sync_menus(
            shop,
            aid,
            [
                {
                    "id": menu.id,
                    "menu_name": menu.menu_name,
                    "memo": menu.memo,
                    "sort_order": menu.sort_order,
                }
                for menu in payload.menus
            ],
        )
        self.repo.sync_keywords(
            shop,
            aid,
            [
                {
                    "id": keyword.id,
                    "keyword": keyword.keyword,
                    "sort_order": keyword.sort_order,
                }
                for keyword in payload.keywords
            ],
        )
        self.repo.sync_stations(
            shop,
            aid,
            [
                {
                    "id": station.id,
                    "transport_line": station.transport_line,
                    "station_name": station.station_name,
                    "walk_minutes": station.walk_minutes,
                    "distance_memo": station.distance_memo,
                    "sort_order": station.sort_order,
                }
                for station in payload.stations
            ],
        )
        self.repo.sync_visits(
            shop,
            aid,
            [
                {
                    "id": visit.id,
                    "visit_date": visit.visit_date,
                    "memo": visit.memo,
                }
                for visit in payload.visits
            ],
        )
        self.repo.sync_images(shop, aid, self._build_image_payloads(shop, aid, payload.images))

    def _build_image_payloads(self, shop, aid: int, images) -> list[dict]:
        active = {img.id: img for img in shop.images if not img.is_deleted}
        payloads: list[dict] = []
        for image in images:
            mime_type = validate_mime_type(image.mime_type)
            data: dict = {
                "id": image.id,
                "file_name": image.file_name,
                "mime_type": mime_type,
                "sort_order": image.sort_order,
            }
            if image.id is not None:
                if image.id not in active:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="指定された画像が見つかりません",
                    )
                if image.data_base64:
                    data["image_data"] = decode_image_base64(image.data_base64)
            else:
                assert image.data_base64 is not None
                data["image_data"] = decode_image_base64(image.data_base64)
            payloads.append(data)
        return payloads
