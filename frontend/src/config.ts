/** Shops API のベース URL（末尾スラッシュなし） */
export const shopsOrigin = (import.meta.env.VITE_SHOPS_ORIGIN as string | undefined) ?? ''

/** ログイン／セッション API のベース URL（末尾スラッシュなし） */
export const loginOrigin = (import.meta.env.VITE_LOGIN_ORIGIN as string | undefined) ?? ''

/** デバッグ時はセッション延長をスキップ */
export const skipSessionExtend =
  (import.meta.env.VITE_SKIP_SESSION_EXTEND as string | undefined) === 'true'

/** メニュー画面 URL（戻るボタン遷移先） */
export const menuPageUrl =
  (import.meta.env.VITE_MENU_PAGE_URL as string | undefined) ?? '/'
