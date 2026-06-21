from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GenreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


class GenreWithCountOut(GenreOut):
    shop_count: int | None = None


class GenreListResponse(BaseModel):
    items: list[GenreWithCountOut]


class GenreCreateInput(BaseModel):
    name: str = Field(max_length=100)
    sort_order: int = 0


class GenreUpdateInput(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    sort_order: int | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "GenreUpdateInput":
        if self.name is None and self.sort_order is None:
            raise ValueError("name または sort_order のいずれかが必要です")
        return self


class GenreResponse(BaseModel):
    genre: GenreOut
