from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Genre(Base):
    __tablename__ = "genres"
    __table_args__ = {"schema": "shops"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    shop_links: Mapped[list["ShopGenre"]] = relationship(back_populates="genre")


class Shop(Base):
    __tablename__ = "shops"
    __table_args__ = (
        UniqueConstraint("id", "aid", name="shops_id_aid_key"),
        {"schema": "shops"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    schedule_memo: Mapped[str | None] = mapped_column(Text)
    last_verified_on: Mapped[date | None] = mapped_column(Date)
    memo: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    genre_links: Mapped[list["ShopGenre"]] = relationship(back_populates="shop")
    opening_days: Mapped[list["ShopOpeningDay"]] = relationship(back_populates="shop")
    menus: Mapped[list["ShopMenu"]] = relationship(back_populates="shop")
    keywords: Mapped[list["ShopKeyword"]] = relationship(back_populates="shop")
    stations: Mapped[list["ShopStation"]] = relationship(back_populates="shop")
    images: Mapped[list["ShopImage"]] = relationship(back_populates="shop")


class ShopGenre(Base):
    __tablename__ = "shop_genres"
    __table_args__ = {"schema": "shops"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shops.id"), nullable=False
    )
    genre_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.genres.id"), nullable=False
    )
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    shop: Mapped["Shop"] = relationship(back_populates="genre_links")
    genre: Mapped["Genre"] = relationship(back_populates="shop_links")


class ShopOpeningDay(Base):
    __tablename__ = "shop_opening_days"
    __table_args__ = {"schema": "shops"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shops.id"), nullable=False
    )
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    day_memo: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    shop: Mapped["Shop"] = relationship(back_populates="opening_days")
    slots: Mapped[list["ShopOpeningSlot"]] = relationship(back_populates="opening_day")


class ShopOpeningSlot(Base):
    __tablename__ = "shop_opening_slots"
    __table_args__ = {"schema": "shops"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opening_day_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shop_opening_days.id"), nullable=False
    )
    shop_id: Mapped[int] = mapped_column(Integer, nullable=False)
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    opening_day: Mapped["ShopOpeningDay"] = relationship(back_populates="slots")


class ShopMenu(Base):
    __tablename__ = "shop_menus"
    __table_args__ = {"schema": "shops"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shops.id"), nullable=False
    )
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    menu_name: Mapped[str] = mapped_column(String(200), nullable=False)
    memo: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    shop: Mapped["Shop"] = relationship(back_populates="menus")


class ShopKeyword(Base):
    __tablename__ = "shop_keywords"
    __table_args__ = {"schema": "shops"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shops.id"), nullable=False
    )
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    shop: Mapped["Shop"] = relationship(back_populates="keywords")


class ShopStation(Base):
    __tablename__ = "shop_stations"
    __table_args__ = {"schema": "shops"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shops.id"), nullable=False
    )
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    transport_type: Mapped[str] = mapped_column(String(50), nullable=False)
    line_name: Mapped[str | None] = mapped_column(String(100))
    station_name: Mapped[str] = mapped_column(String(100), nullable=False)
    walk_minutes: Mapped[int | None] = mapped_column(SmallInteger)
    distance_memo: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    shop: Mapped["Shop"] = relationship(back_populates="stations")


class ShopImage(Base):
    __tablename__ = "shop_images"
    __table_args__ = {"schema": "shops"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shops.shops.id"), nullable=False
    )
    aid: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    image_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    shop: Mapped["Shop"] = relationship(back_populates="images")
