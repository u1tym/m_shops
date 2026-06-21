/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BASE_PATH: string
  readonly VITE_SHOPS_ORIGIN: string
  readonly VITE_LOGIN_ORIGIN: string
  readonly VITE_MENU_PAGE_URL: string
  readonly VITE_SKIP_SESSION_EXTEND: string
  readonly VITE_SHOPS_PROXY_TARGET: string
  readonly VITE_LOGIN_PROXY_TARGET: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
