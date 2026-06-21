import { reactive } from 'vue'

import { loginOrigin, skipSessionExtend } from '../config'
import { isUnauthorizedError } from './auth'
import { postLogin, postRefresh } from './loginApi'

export class SessionAuthCancelledError extends Error {
  constructor(message = 'ログインが必要です') {
    super(message)
    this.name = 'SessionAuthCancelledError'
  }
}

export const sessionLoginDialog = reactive({
  open: false,
  username: '',
  password: '',
  error: null as string | null,
  loading: false,
})

let cachedUsername = ''
let loginDialogPromise: Promise<boolean> | null = null
let loginDialogResolve: ((success: boolean) => void) | null = null

function finishLoginDialog(success: boolean): void {
  sessionLoginDialog.open = false
  sessionLoginDialog.loading = false
  loginDialogResolve?.(success)
  loginDialogResolve = null
  loginDialogPromise = null
}

function openLoginDialog(): Promise<boolean> {
  if (loginDialogPromise) {
    return loginDialogPromise
  }

  sessionLoginDialog.username = cachedUsername
  sessionLoginDialog.password = ''
  sessionLoginDialog.error = null
  sessionLoginDialog.loading = false
  sessionLoginDialog.open = true

  loginDialogPromise = new Promise<boolean>((resolve) => {
    loginDialogResolve = resolve
  })
  return loginDialogPromise
}

export async function submitSessionLogin(): Promise<void> {
  const username = sessionLoginDialog.username.trim()
  const password = sessionLoginDialog.password
  if (!username || !password) {
    sessionLoginDialog.error = 'ユーザー名とパスワードを入力してください'
    return
  }

  sessionLoginDialog.loading = true
  sessionLoginDialog.error = null
  try {
    await postLogin(username, password)
    cachedUsername = username
    finishLoginDialog(true)
  } catch (error) {
    sessionLoginDialog.loading = false
    if (isUnauthorizedError(error)) {
      sessionLoginDialog.error = 'ユーザー名またはパスワードが正しくありません'
      return
    }
    sessionLoginDialog.error = 'ログインに失敗しました'
  }
}

export function cancelSessionLogin(): void {
  finishLoginDialog(false)
}

async function tryRefreshSession(): Promise<boolean> {
  try {
    await postRefresh()
    return true
  } catch (error) {
    if (isUnauthorizedError(error)) {
      return false
    }
    throw error
  }
}

export async function ensureSessionValid(): Promise<void> {
  if (skipSessionExtend || !loginOrigin) {
    return
  }

  if (await tryRefreshSession()) {
    return
  }

  const loggedIn = await openLoginDialog()
  if (!loggedIn) {
    throw new SessionAuthCancelledError()
  }
}
