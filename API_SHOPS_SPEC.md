# お店管理 API 仕様書

## 1. 概要

| 項目 | 内容 |
|------|------|
| 役割 | ログインユーザーごとのお店情報・ジャンルの CRUD、検索、参考画像の取得 |
| 実装予定 | Python / FastAPI |
| 想定 URL | Nginx 経由で `/api/shops` 以下（バックエンドでは `/shops` 等） |
| 認証方式 | 認証 API が発行した JWT（HttpOnly Cookie）を検証するのみ（本 API は JWT を発行しない） |
| データベース | `shops` スキーマ（詳細は `DB_SHOPS_SPEC.md`） |

### 1.1 機能一覧

| 区分 | 機能 |
|------|------|
| 店舗 | 一覧表示、追加、編集、削除（論理削除）、検索（駅・場所） |
| ジャンル | 追加、編集、削除（論理削除）、一覧取得 |
| 地図 | 住所から Google マップ表示用 URL を生成して返す |
| 画像 | 店舗登録・編集時の画像取り込み、個別画像のバイナリ取得 |

---

## 2. 認証・認可

### 2.1 認証

| 項目 | 内容 |
|------|------|
| 検証クラス | `JWTVerifier`（`auth_api/app/security/jwt_verifier.py`） |
| Cookie 名 | 環境変数 `COOKIE_NAME`（既定 `access_token`） |
| ユーザー ID | JWT クレーム `sub` を整数に変換し、`aid`（= `public.accounts.id`）として利用 |

認証 API の詳細は `API_LOGIN_SPEC.md` を参照すること。

### 2.2 認可ルール

- すべての業務 API（`/health` を除く）は **ログイン必須**
- 読み書き対象は常に **`aid = 自分の accounts.id`** かつ **`is_deleted = false`** の行に限定する
- 他ユーザーの `shop_id` / `genre_id` 等へのアクセスは **404 Not Found** とする（存在漏洩を避ける）

### 2.3 CORS

- `Access-Control-Allow-Credentials: true`
- `Allow-Origin` は `CORS_ORIGINS` に列挙したオリジンのみ
- フロントエンド（Vue + axios）では `withCredentials: true` が必要

---

## 3. 共通仕様

### 3.1 URL の考え方

Nginx で `location /api/shops/ { proxy_pass http://shops/; }` のように切り出す場合、クライアントは **`/api/shops/...`** にアクセスする。  
下表の「アプリパス」は FastAPI アプリ上のパス（プレフィックス `/shops` を付与する想定）。

| 種別 | クライアント例 | アプリパス例 |
|------|----------------|--------------|
| 店舗一覧 | `GET /api/shops/shops` | `GET /shops` |
| ヘルスチェック | `GET /api/shops/health` | `GET /health` |

※ 実装時にルーターの `prefix` と Nginx の `proxy_pass` を揃えること。本書では **アプリパス** を基準に記載する。

### 3.2 日時・時刻の形式

| 種別 | 形式 | 例 |
|------|------|-----|
| 日付 | ISO 8601 日付 | `"2026-06-21"` |
| 時刻 | `HH:MM`（24 時間制） | `"11:30"` |
| タイムスタンプ | ISO 8601（タイムゾーンなし） | `"2026-06-21T12:34:56"` |

### 3.3 曜日（`day_of_week`）

`DB_SHOPS_SPEC.md` と同一。

| 値 | 曜日 |
|----|------|
| 0 | 日曜 |
| 1 | 月曜 |
| 2 | 火曜 |
| 3 | 水曜 |
| 4 | 木曜 |
| 5 | 金曜 |
| 6 | 土曜 |

### 3.4 エラーレスポンス

FastAPI 既定の JSON 形式。

```json
{ "detail": "メッセージまたは検証エラー内容" }
```

バリデーションエラー（422）時は `detail` がオブジェクト配列になる場合がある。

| HTTP | 用途 |
|------|------|
| 400 | 業務ルール違反（画像サイズ超過、時刻不正など） |
| 401 | 未ログイン、JWT 不正・期限切れ |
| 404 | 対象リソースなし（他ユーザー所有を含む） |
| 409 | 一意制約違反（同名ジャンル、同一キーワードなど） |
| 422 | リクエスト形式・型の不正 |

### 3.5 論理削除

| リソース | DELETE 時の動作 |
|----------|-----------------|
| 店舗 | `shops.is_deleted = true`。子テーブルは行を残す |
| ジャンル | `genres.is_deleted = true`。`shop_genres` は行を残し、表示時にジャンル名を「（削除済み）」等とする |

削除済みリソースは GET 一覧・詳細・検索の対象外とする。

### 3.6 Google マップ URL

住所（`address`）が設定されている店舗について、レスポンスに **`google_maps_url`** を付与する。

| 項目 | 内容 |
|------|------|
| 生成式 | `https://www.google.com/maps/search/?api=1&query={URLエンコードした address}` |
| Geocoding API | **使用しない**（初版は住所文字列による検索 URL のみ） |
| フロントエンド | 返却 URL を新規タブまたは iframe で開いて地図表示する |

一覧・詳細・検索の各レスポンスで、`address` が NULL の場合は `google_maps_url` も `null` とする。

### 3.7 参考画像の受け渡し

DB には `bytea` で保存する。API では次の 2 方式を使い分ける。

| 操作 | 方式 |
|------|------|
| 登録・更新 | JSON 内に **Base64 文字列**（クリップボード貼り付け対応） |
| 参照 | 専用 GET で **バイナリ**（`Content-Type: image/...`）を返す |

**画像入力オブジェクト（登録・更新用）**

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `id` | integer | いいえ | 既存画像の更新時のみ指定。未指定なら新規追加 |
| `file_name` | string | いいえ | 表示用ファイル名 |
| `mime_type` | string | はい | 例: `image/png`, `image/jpeg` |
| `data_base64` | string | 新規時は必須 | Base64 本体。`data:image/png;base64,...` 形式も可（サーバー側でプレフィックス除去） |
| `sort_order` | integer | いいえ | 既定 `0` |

**制約**

- 1 枚あたり **5MB（5,242,880 バイト）** 以下
- 許可 MIME: `image/jpeg`, `image/png`, `image/webp`, `image/gif`
- 店舗編集時、リクエストの `images` 配列に含まれない既存画像 ID は **論理削除** する（配列で全件指定＝置換方式）

---

## 4. データモデル（API 上の JSON）

### 4.1 ジャンル `Genre`

```json
{
  "id": 1,
  "name": "ラーメン",
  "sort_order": 0,
  "created_at": "2026-06-21T10:00:00",
  "updated_at": "2026-06-21T10:00:00"
}
```

### 4.2 営業時間スロット `OpeningSlot`

```json
{
  "open_time": "11:00",
  "close_time": "14:00",
  "sort_order": 0
}
```

- `open_time` と `close_time` が同一の場合は 400 エラー
- `close_time < open_time` は翌日終了として扱う（表示用ラベルはフロントエンド任せ）

### 4.3 曜日別営業 `OpeningDay`

```json
{
  "day_of_week": 1,
  "day_memo": "第2・第4水曜は休み",
  "slots": [
    { "open_time": "11:00", "close_time": "14:00", "sort_order": 0 },
    { "open_time": "17:00", "close_time": "22:00", "sort_order": 1 }
  ]
}
```

- **定休日**: `slots` を空配列とし、必要なら `day_memo` に記述
- 曜日に依存しないメモ（祝日休みなど）は店舗の `schedule_memo`

### 4.4 その他の子要素

**メニュー `Menu`**

```json
{ "id": 10, "menu_name": "味噌ラーメン", "memo": "辛め", "sort_order": 0 }
```

**キーワード `Keyword`**

```json
{ "id": 20, "keyword": "禁煙", "sort_order": 0 }
```

**最寄り駅 `Station`**

```json
{
  "id": 30,
  "transport_type": "電車",
  "line_name": "JR山手線",
  "station_name": "渋谷",
  "walk_minutes": 5,
  "distance_memo": "ハチ公口",
  "sort_order": 0
}
```

**画像メタデータ `ImageMeta`（一覧・詳細用）**

```json
{
  "id": 40,
  "file_name": "photo.png",
  "mime_type": "image/png",
  "file_size_bytes": 102400,
  "sort_order": 0,
  "url": "/api/shops/shops/1/images/40"
}
```

`url` はクライアントがそのまま GET できるパス（Nginx 経由のフルパス）。

### 4.5 店舗サマリ `ShopSummary`（一覧・検索）

```json
{
  "id": 1,
  "name": "麺屋 示例",
  "address": "東京都渋谷区...",
  "google_maps_url": "https://www.google.com/maps/search/?api=1&query=...",
  "schedule_memo": "祝日休み",
  "last_verified_on": "2026-06-01",
  "memo": null,
  "genres": [
    { "id": 1, "name": "ラーメン", "sort_order": 0 }
  ],
  "stations": [
    {
      "id": 30,
      "station_name": "渋谷",
      "transport_type": "電車",
      "walk_minutes": 5,
      "sort_order": 0
    }
  ],
  "created_at": "2026-06-21T10:00:00",
  "updated_at": "2026-06-21T10:00:00"
}
```

一覧では子要素のうち **ジャンル** と **最寄り駅（簡略）** のみ含める。営業時間・メニュー・キーワード・画像は詳細 API で取得する。

### 4.6 店舗詳細 `ShopDetail`

`ShopSummary` のフィールドに加え、以下を含む。

```json
{
  "opening_days": [ /* OpeningDay[] */ ],
  "menus": [ /* Menu[] */ ],
  "keywords": [ /* Keyword[] */ ],
  "stations": [ /* Station 完全形[] */ ],
  "images": [ /* ImageMeta[] */ ]
}
```

---

## 5. 店舗 API

### 5.1 `GET /shops`

店舗一覧。検索クエリを付与した場合は条件絞り込みも兼ねる。

**認証**: 必須

**クエリパラメータ**

| パラメータ | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `station` | string | いいえ | 駅名の **部分一致**（`shop_stations.station_name`） |
| `location` | string | いいえ | 場所の **部分一致**（`shops.address` および `shops.name`） |
| `keyword` | string | いいえ | キーワードの部分一致 |
| `genre_id` | integer | いいえ | ジャンル ID による絞り込み |
| `q` | string | いいえ | 店名・住所・キーワード・駅名を横断する汎用検索（部分一致） |
| `page` | integer | いいえ | ページ番号。既定 `1` |
| `per_page` | integer | いいえ | 1 ページ件数。既定 `20`、最大 `100` |

**検索の組み合わせ**

- 複数パラメータ指定時は **AND 条件**
- `station` と `location` はユーザーの「駅や場所を指定」検索に対応する主要パラメータ
- `q` 指定時は `station` / `location` / `keyword` より **優先** し、`q` のみで横断検索する（他の絞り込みパラメータは無視）

**レスポンス `200`**

```json
{
  "items": [ /* ShopSummary[] */ ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
```

**ソート**

- 既定: `updated_at` 降順（最近更新した店を先に）

---

### 5.2 `GET /shops/{shop_id}`

店舗詳細。

**認証**: 必須

**パスパラメータ**

| 名前 | 型 | 説明 |
|------|-----|------|
| `shop_id` | integer | 店舗 ID |

**レスポンス `200`**

```json
{ "shop": { /* ShopDetail */ } }
```

**エラー `404`**

- 店舗なし、削除済み、他ユーザー所有

---

### 5.3 `POST /shops`

店舗の新規登録。子要素（営業時間・メニュー・キーワード・駅・画像・ジャンル）をまとめて登録する。

**認証**: 必須

**リクエスト JSON**

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `name` | string | はい | 店名（最大 200 文字） |
| `address` | string | いいえ | 住所 |
| `schedule_memo` | string | いいえ | 曜日に限らない営業メモ |
| `last_verified_on` | string (date) | いいえ | 最終確認日 |
| `memo` | string | いいえ | 汎用メモ |
| `genre_ids` | integer[] | いいえ | 付与するジャンル ID の配列 |
| `opening_days` | OpeningDay[] | いいえ | 曜日別営業時間 |
| `menus` | object[] | いいえ | `{ menu_name, memo?, sort_order? }` |
| `keywords` | object[] | いいえ | `{ keyword, sort_order? }` |
| `stations` | object[] | いいえ | Station から `id` を除いた形 |
| `images` | ImageInput[] | いいえ | §3.7 の画像入力 |

**レスポンス `201`**

```json
{ "shop": { /* ShopDetail */ } }
```

**エラー**

| HTTP | 条件 |
|------|------|
| 400 | バリデーション・画像サイズ超過・時刻不正 |
| 404 | `genre_ids` に存在しないまたは他ユーザー所有の ID が含まれる |
| 409 | 同一店舗内でキーワード重複など |

---

### 5.4 `PUT /shops/{shop_id}`

店舗の更新。基本情報および子要素を **リクエスト内容で置換** する。

**認証**: 必須

**リクエスト JSON**

`POST /shops` と同一構造。`genre_ids`、`opening_days`、`menus`、`keywords`、`stations`、`images` は、送信された配列が新しい完全な状態を表す。

**子要素の更新ルール**

| 子要素 | ルール |
|--------|--------|
| `genre_ids` | 送信配列で `shop_genres` を再構成（外れた関連は論理削除） |
| `opening_days` | 曜日単位で置換。既存 `opening_day_id` は維持せず、送信内容から再生成してよい |
| `menus` / `keywords` / `stations` | 送信に含まれない既存 ID は論理削除。`id` 付きは更新、なしは新規 |
| `images` | §3.7 の置換方式 |

**レスポンス `200`**

```json
{ "shop": { /* ShopDetail */ } }
```

**エラー**

`POST /shops` と同様。

---

### 5.5 `DELETE /shops/{shop_id}`

店舗の論理削除。

**認証**: 必須

**レスポンス `200`**

```json
{ "message": "ok" }
```

**エラー `404`**

- 店舗なし、削除済み、他ユーザー所有

---

### 5.6 `GET /shops/{shop_id}/images/{image_id}`

参考画像のバイナリ取得。

**認証**: 必須

**レスポンス `200`**

| ヘッダ | 値 |
|--------|-----|
| `Content-Type` | 画像の `mime_type`（例: `image/png`） |
| `Content-Length` | バイトサイズ |

ボディは画像バイナリ（JSON ではない）。

**エラー `404`**

- 画像なし、削除済み、店舗不一致、他ユーザー所有

---

## 6. ジャンル API

### 6.1 `GET /genres`

ジャンル一覧。

**認証**: 必須

**クエリパラメータ**

| パラメータ | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `include_usage_count` | boolean | いいえ | `true` のとき各ジャンルの店舗数 `shop_count` を付与。既定 `false` |

**レスポンス `200`**

```json
{
  "items": [
    {
      "id": 1,
      "name": "ラーメン",
      "sort_order": 0,
      "shop_count": 3,
      "created_at": "2026-06-21T10:00:00",
      "updated_at": "2026-06-21T10:00:00"
    }
  ]
}
```

**ソート**

- 既定: `sort_order` 昇順 → `name` 昇順

---

### 6.2 `POST /genres`

ジャンルの追加。

**認証**: 必須

**リクエスト JSON**

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `name` | string | はい | ジャンル名（最大 100 文字） |
| `sort_order` | integer | いいえ | 既定 `0` |

**レスポンス `201`**

```json
{ "genre": { /* Genre */ } }
```

**エラー `409`**

- 同一ユーザー内で同名ジャンルが既に存在（未削除）

---

### 6.3 `PATCH /genres/{genre_id}`

ジャンルの編集。

**認証**: 必須

**リクエスト JSON**

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `name` | string | いいえ | ジャンル名 |
| `sort_order` | integer | いいえ | 表示順 |

※ 少なくとも 1 フィールド必須。

**レスポンス `200`**

```json
{ "genre": { /* Genre */ } }
```

**エラー**

| HTTP | 条件 |
|------|------|
| 404 | ジャンルなし、削除済み、他ユーザー所有 |
| 409 | 改名先が同一ユーザー内で重複 |

---

### 6.4 `DELETE /genres/{genre_id}`

ジャンルの論理削除。

**認証**: 必須

**レスポンス `200`**

```json
{ "message": "ok" }
```

**補足**

- 店舗に紐づいたまま `shop_genres` は残る
- 店舗詳細・一覧では、削除済みジャンルは `name` を `"（削除済み）"` 等に置き換えて返す

**エラー `404`**

- ジャンルなし、削除済み、他ユーザー所有

---

## 7. 地図表示（フロントエンド連携）

本 API は Google Maps Platform の API キーを **使用しない**。フロントエンドは次の手順で地図を表示する。

### 7.1 単一店舗の地図

1. `GET /shops/{shop_id}` または一覧の `google_maps_url` を利用
2. `google_maps_url` が非 NULL なら、リンクまたは `window.open` で Google マップを開く

### 7.2 検索結果の地図一覧表示

1. `GET /shops?station=...` または `GET /shops?location=...` で店舗一覧を取得
2. `address` が設定されている店舗について、各 `google_maps_url` を地図 UI（リスト＋「地図で開く」ボタン等）に表示
3. 複数店舗を 1 つの地図にマーカー表示する場合は、フロントエンドで Google Maps JavaScript API 等を別途導入する（初版 API の範囲外）

---

## 8. エンドポイント一覧

| メソッド | アプリパス | 説明 | 認証 |
|----------|------------|------|------|
| GET | `/health` | 稼働確認 | 不要 |
| GET | `/shops` | 店舗一覧・検索 | 必須 |
| GET | `/shops/{shop_id}` | 店舗詳細 | 必須 |
| POST | `/shops` | 店舗追加 | 必須 |
| PUT | `/shops/{shop_id}` | 店舗編集 | 必須 |
| DELETE | `/shops/{shop_id}` | 店舗削除 | 必須 |
| GET | `/shops/{shop_id}/images/{image_id}` | 参考画像取得 | 必須 |
| GET | `/genres` | ジャンル一覧 | 必須 |
| POST | `/genres` | ジャンル追加 | 必須 |
| PATCH | `/genres/{genre_id}` | ジャンル編集 | 必須 |
| DELETE | `/genres/{genre_id}` | ジャンル削除 | 必須 |

---

## 9. 実装メモ（FastAPI）

### 9.1 推奨ディレクトリ構成（案）

```
backend/
  app/
    main.py
    config.py
    database.py
    dependencies.py      # JWT 検証、aid 取得
    routers/
      shops.py
      genres.py
      health.py
    schemas/             # Pydantic モデル
    services/            # 業務ロジック
    repositories/        # DB アクセス
```

### 9.2 JWT 検証の利用例

```python
from fastapi import Depends
from auth_api.app.security.jwt_verifier import JWTVerifier

verifier = JWTVerifier(secret_key="...", algorithm="HS256", cookie_name="access_token")
require_user = verifier.dependency()

def get_aid(claims: dict = Depends(require_user)) -> int:
    return int(claims["sub"])
```

### 9.3 トランザクション

- `POST /shops`、`PUT /shops/{shop_id}` は店舗本体と子テーブルを **1 トランザクション** で処理する
- 途中でエラーがあればロールバック

### 9.4 環境変数

認証 API と共通のものに加え、DB 接続は `.env` の `DB_HOST` 等を利用（`API_LOGIN_SPEC.md` 参照）。

| 環境変数 | 説明 |
|----------|------|
| `SECRET_KEY` | JWT 検証用（認証 API と同一） |
| `ALGORITHM` | 既定 `HS256` |
| `COOKIE_NAME` | 既定 `access_token` |
| `CORS_ORIGINS` | カンマ区切りオリジン |

---

## 10. 確定した設計方針

| # | 項目 | 方針 |
|---|------|------|
| 1 | 店舗の作成・更新 | 子要素込みの **一括 JSON**（`POST` / `PUT`） |
| 2 | 店舗検索 | `station`（駅名）・`location`（住所・店名）の部分一致。汎用 `q` も提供 |
| 3 | 画像 | 登録・更新は Base64 JSON、取得はバイナリ GET |
| 4 | Google マップ | Geocoding API は使わず、`google_maps_url` をサーバーで生成 |
| 5 | ジャンルと店舗 | 多対多。店舗側は `genre_ids` で指定 |
| 6 | 削除 | 店舗・ジャンルとも論理削除 |

---

## 11. 関連ファイル

| ファイル | 内容 |
|----------|------|
| `DB_SHOPS_SPEC.md` | DB テーブル仕様 |
| `DB/1_db.sql` | DDL |
| `API_LOGIN_SPEC.md` | 認証 API・JWT 仕様 |
| `JWT_USERNAME_TECH_SPEC.md` | JWT クレーム等の補足 |

---

## 12. 確認事項（将来拡張）

初版では実装しないが、必要になったら追記する項目。

| 項目 | 内容 |
|------|------|
| 緯度・経度 | Google Geocoding API 連携し、地図上へのマーカー一括表示 |
| 画像の個別 DELETE | 現状は `PUT /shops` の `images` 置換で削除 |
| ジャンル一覧のページング | 件数が少ない前提で省略 |
