# お店管理 API（バックエンド）

PostgreSQL + FastAPI で動作するお店管理 API です。店舗・ジャンルの CRUD、検索、参考画像の取得を提供します。

API の詳細仕様はリポジトリ直下の [`API_SHOPS_SPEC.md`](../API_SHOPS_SPEC.md)、DB 設計は [`DB_SHOPS_SPEC.md`](../DB_SHOPS_SPEC.md) を参照してください。

## 必要な環境

| 項目 | バージョン目安 |
|------|----------------|
| Python | 3.11 以上推奨 |
| PostgreSQL | 14 以上推奨 |

`public.accounts` テーブルが存在すること（`shops` スキーマの外部キー先）が前提です。

## ディレクトリ構成

```
backend/
  app/
    main.py           # FastAPI アプリのエントリポイント
    config.py         # 環境変数の読み込み
    database.py       # DB 接続
    dependencies.py   # 認証（aid 取得）
    models.py         # SQLAlchemy モデル
    routers/          # HTTP エンドポイント
    services/         # 業務ロジック
    repositories/     # DB アクセス
    schemas/          # リクエスト／レスポンス型
    security/         # JWT 検証
  requirements.txt
  .env                # 環境変数（git 管理外）
  README.md
```

## セットアップ

### 1. データベースの準備

`shops` スキーマとテーブルを作成します。

```powershell
psql -h localhost -U tamtuser -d tamtdb -f ..\DB\1_db.sql
```

接続情報は環境に合わせて読み替えてください。

### 2. 仮想環境の作成と依存パッケージのインストール

**uvicorn だけ入っていても起動できません。** `requirements.txt` のパッケージをすべてインストールしてください。

**Windows（PowerShell）**

```powershell
cd backend
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS**

```bash
cd backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

インストール確認:

```bash
python -c "import pydantic_settings; print('ok')"
```

`ok` と表示されれば依存パッケージは揃っています。

### 3. 環境変数（`.env`）の設定

`backend` フォルダ直下に `.env` を作成します（`.gitignore` 対象のため、各自で用意してください）。

```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tamtdb
DB_USER=tamtuser
DB_PASSWORD=your_password

# デバッグ（後述）
DEBUG=true
DEBUG_AID=1

# JWT（本番では認証 API と同じ SECRET_KEY を設定）
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
COOKIE_NAME=access_token

# フロントエンドのオリジン（カンマ区切り）
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173

# クライアントから見た公開パス（参考用。Nginx 設定と揃える）
API_PUBLIC_PREFIX=/api/shops
```

## 起動方法

### 開発（ホットリロードあり）

仮想環境を有効化したうえで、`backend` ディレクトリから起動します。

**Windows（PowerShell）**

```powershell
cd backend
.\env\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Linux / macOS**

```bash
cd backend
source env/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 9012 --reload
```

ポート番号は環境に合わせて変更してください（例: `9012`）。

起動後、次の URL で確認できます。

| URL | 内容 |
|-----|------|
| http://127.0.0.1:8000/health | ヘルスチェック |
| http://127.0.0.1:8000/docs | Swagger UI（API ドキュメント） |
| http://127.0.0.1:8000/redoc | ReDoc |

フロントエンド（Vite）からは、プロキシ経由で `http://127.0.0.1:8000` に接続する想定です（`frontend/.env.development` の `VITE_SHOPS_PROXY_TARGET`）。

### 本番

Uvicorn ワーカー付き Gunicorn で起動する例です。ホスト・ポート・ワーカー数は環境に合わせて調整してください。

```powershell
.\env\Scripts\gunicorn.exe app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

本番では `DEBUG=false` とし、リバースプロキシ（Nginx 等）で `/api/shops` 以下に振り分ける構成を想定しています。

## 認証

本 API は JWT を**発行しません**。別途用意した認証 API が HttpOnly Cookie に載せた JWT を検証します。

| 項目 | 内容 |
|------|------|
| Cookie 名 | `COOKIE_NAME`（既定: `access_token`） |
| ユーザー ID | JWT の `sub` を整数化し、`aid`（= `public.accounts.id`）として利用 |
| 認可 | 常に自分の `aid` に紐づくデータのみ操作可能 |

### デバッグモード

`.env` で `DEBUG=true` のときは JWT 検証をスキップし、`DEBUG_AID` の値を `aid` として使います。ローカル開発・単体テスト向けの設定です。

**本番環境では必ず `DEBUG=false` にしてください。**

## 主なエンドポイント

アプリ上のパス（ルート）です。Nginx で `/api/shops` にマウントする場合、クライアントからは `/api/shops` を前置した URL になります。

| メソッド | パス | 概要 |
|----------|------|------|
| GET | `/health` | 死活監視（認証不要） |
| GET | `/shops` | 店舗一覧・検索 |
| POST | `/shops` | 店舗作成 |
| GET | `/shops/{id}` | 店舗詳細 |
| PUT | `/shops/{id}` | 店舗更新 |
| DELETE | `/shops/{id}` | 店舗削除（論理削除） |
| GET | `/shops/{id}/images/{image_id}` | 参考画像バイナリ取得 |
| GET | `/genres` | ジャンル一覧 |
| POST | `/genres` | ジャンル作成 |
| PATCH | `/genres/{id}` | ジャンル更新 |
| DELETE | `/genres/{id}` | ジャンル削除（論理削除） |

### 店舗検索クエリ（`GET /shops`）の例

| パラメータ | 説明 |
|------------|------|
| `search` | 店名・キーワードの部分一致 |
| `genre_id` | ジャンル ID で絞り込み |
| `open_day_of_week` | 営業曜日（0=日 … 6=土） |
| `open_time` | 営業時刻（`HH:MM`）。曜日とセットで指定 |
| `has_image` | 一覧で参考画像を表示するか（`true` のみ `thumbnail` を返す。件数には影響しない） |
| `station` / `location` / `keyword` / `q` | その他の検索条件 |
| `page` / `per_page` | ページング |

## 動作確認の例

```powershell
# ヘルスチェック
curl http://127.0.0.1:8000/health

# 店舗一覧（DEBUG=true のとき認証不要）
curl http://127.0.0.1:8000/shops

# ジャンル一覧
curl http://127.0.0.1:8000/genres
```

## トラブルシューティング

| 症状 | 確認すること |
|------|----------------|
| `ModuleNotFoundError: No module named 'pydantic_settings'` 等 | `pip install -r requirements.txt` を実行したか。仮想環境を有効化してから起動しているか（`which uvicorn` / `where uvicorn` でパスを確認） |
| DB 接続エラー | `.env` の接続情報、PostgreSQL の起動、`shops` スキーマの作成 |
| 401 Unauthorized | `DEBUG=false` のときは Cookie 付きリクエストが必要。開発時は `DEBUG=true` を確認 |
| CORS エラー | `CORS_ORIGINS` にフロントエンドのオリジンが含まれているか |
| 外部キー制約エラー | `public.accounts` に `DEBUG_AID` 相当の行が存在するか |

## 関連ドキュメント

- [`API_SHOPS_SPEC.md`](../API_SHOPS_SPEC.md) — API 仕様
- [`DB_SHOPS_SPEC.md`](../DB_SHOPS_SPEC.md) — DB 設計
- [`DB/1_db.sql`](../DB/1_db.sql) — DDL
