-- 店舗に都道府県カラムを追加
-- 既存 DB 向けマイグレーション

ALTER TABLE shops.shops
    ADD COLUMN IF NOT EXISTS prefecture character varying(10);

CREATE INDEX IF NOT EXISTS ix_shops_aid_prefecture_active
    ON shops.shops (aid, prefecture)
    WHERE is_deleted = false;
