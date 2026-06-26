export const DAY_LABELS = ['日', '月', '火', '水', '木', '金', '土'] as const

export function buildMapQuery(address: string, prefecture?: string | null): string {
  const trimmed = address.trim()
  const pref = prefecture?.trim()
  if (pref && trimmed) {
    return `${pref}${trimmed}`
  }
  return pref || trimmed
}

/** Google マップ埋め込み URL（q= で住所を指定し、マーカー付きで表示） */
export function mapsEmbedUrl(address: string, prefecture?: string | null): string {
  const query = buildMapQuery(address, prefecture)
  return `https://maps.google.com/maps?q=${encodeURIComponent(query)}&z=15&output=embed`
}

export function newKey(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

export function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(blob)
  })
}
