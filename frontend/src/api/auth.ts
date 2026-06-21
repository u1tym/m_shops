import axios from 'axios'

export function isUnauthorizedError(error: unknown): boolean {
  return axios.isAxiosError(error) && error.response?.status === 401
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d) => d.msg ?? JSON.stringify(d)).join(', ')
    }
    return error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'エラーが発生しました'
}
