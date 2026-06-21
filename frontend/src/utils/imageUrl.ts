import { shopsOrigin } from '../config'

export function resolveShopImagePath(url: string): string {
  if (shopsOrigin && url.startsWith(shopsOrigin)) {
    return url.slice(shopsOrigin.length) || '/'
  }
  const marker = '/shops/'
  const idx = url.indexOf(marker)
  if (idx >= 0) {
    return url.slice(idx)
  }
  return url
}
