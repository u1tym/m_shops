import { ensureSessionValid } from './sessionAuth'

export async function extendSession(): Promise<void> {
  await ensureSessionValid()
}
