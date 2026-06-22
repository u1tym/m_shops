from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MessageResponse(BaseModel):
    message: str


class OpeningSlotInput(BaseModel):
    open_time: time
    close_time: time
    sort_order: int = 0

    @model_validator(mode="after")
    def validate_times(self) -> "OpeningSlotInput":
        if self.open_time == self.close_time:
            raise ValueError("open_time と close_time は同一にできません")
        return self


class OpeningSlotOut(BaseModel):
    open_time: str
    close_time: str
    sort_order: int


class OpeningDayInput(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    day_memo: str | None = None
    is_closed: bool = False
    slots: list[OpeningSlotInput] = Field(default_factory=list)


class OpeningDayOut(BaseModel):
    day_of_week: int
    day_memo: str | None
    is_closed: bool
    slots: list[OpeningSlotOut]


class HolidayHoursInput(BaseModel):
    is_closed: bool = False
    memo: str | None = None
    slots: list[OpeningSlotInput] = Field(default_factory=list)


class HolidayHoursOut(BaseModel):
    is_closed: bool
    memo: str | None
    slots: list[OpeningSlotOut]


class MenuInput(BaseModel):
    id: int | None = None
    menu_name: str = Field(max_length=200)
    memo: str | None = None
    sort_order: int = 0


class MenuOut(BaseModel):
    id: int
    menu_name: str
    memo: str | None
    sort_order: int


class KeywordInput(BaseModel):
    id: int | None = None
    keyword: str = Field(max_length=100)
    sort_order: int = 0


class KeywordOut(BaseModel):
    id: int
    keyword: str
    sort_order: int


class StationInput(BaseModel):
    id: int | None = None
    transport_line: str = Field(max_length=150)
    station_name: str = Field(max_length=100)
    walk_minutes: int | None = Field(default=None, ge=0)
    distance_memo: str | None = None
    sort_order: int = 0


class StationSummaryOut(BaseModel):
    id: int
    station_name: str
    transport_line: str
    walk_minutes: int | None
    sort_order: int


class StationOut(StationSummaryOut):
    distance_memo: str | None


class VisitInput(BaseModel):
    id: int | None = None
    visit_date: date
    memo: str | None = None


class VisitOut(BaseModel):
    id: int
    visit_date: date
    memo: str | None


class ImageInput(BaseModel):
    id: int | None = None
    file_name: str | None = Field(default=None, max_length=255)
    mime_type: str = Field(max_length=100)
    data_base64: str | None = None
    sort_order: int = 0

    @model_validator(mode="after")
    def validate_data(self) -> "ImageInput":
        if self.id is None and not self.data_base64:
            raise ValueError("新規画像には data_base64 が必要です")
        return self


class ImageMetaOut(BaseModel):
    id: int
    file_name: str | None
    mime_type: str
    file_size_bytes: int
    sort_order: int
    url: str


class GenreRefOut(BaseModel):
    id: int
    name: str
    sort_order: int


class ShopBaseInput(BaseModel):
    name: str = Field(max_length=200)
    address: str | None = None
    schedule_memo: str | None = None
    last_verified_on: date | None = None
    memo: str | None = None
    genre_ids: list[int] = Field(default_factory=list)
    opening_days: list[OpeningDayInput] = Field(default_factory=list)
    holiday_hours: HolidayHoursInput | None = None
    menus: list[MenuInput] = Field(default_factory=list)
    keywords: list[KeywordInput] = Field(default_factory=list)
    stations: list[StationInput] = Field(default_factory=list)
    visits: list[VisitInput] = Field(default_factory=list)
    images: list[ImageInput] = Field(default_factory=list)


class ShopCreateInput(ShopBaseInput):
    pass


class ShopUpdateInput(ShopBaseInput):
    pass


class ShopSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str | None
    google_maps_url: str | None
    schedule_memo: str | None
    last_verified_on: date | None
    last_visit_on: date | None
    memo: str | None
    genres: list[GenreRefOut]
    stations: list[StationSummaryOut]
    thumbnail: ImageMetaOut | None = None
    created_at: datetime
    updated_at: datetime


class ShopDetailOut(ShopSummaryOut):
    opening_days: list[OpeningDayOut]
    holiday_hours: HolidayHoursOut | None
    menus: list[MenuOut]
    keywords: list[KeywordOut]
    stations: list[StationOut]
    visits: list[VisitOut]
    images: list[ImageMetaOut]


class ShopListResponse(BaseModel):
    items: list[ShopSummaryOut]
    total: int
    page: int
    per_page: int


class ShopDetailResponse(BaseModel):
    shop: ShopDetailOut
