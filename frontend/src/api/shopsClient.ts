import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

import { shopsOrigin, skipSessionExtend } from '../config'
import { isUnauthorizedError } from './auth'
import { extendSession } from './session'
import type {
  Genre,
  GenreListResponse,
  ShopDetailResponse,
  ShopListResponse,
  ShopSearchParams,
  ShopWriteInput,
} from './types'

type RetryableConfig = InternalAxiosRequestConfig & {
  _authRetried?: boolean
}

let sessionExtendPromise: Promise<void> | null = null

async function ensureSessionExtended(): Promise<void> {
  if (!sessionExtendPromise) {
    sessionExtendPromise = extendSession().finally(() => {
      sessionExtendPromise = null
    })
  }
  await sessionExtendPromise
}

async function shopsRequestInterceptor(
  config: InternalAxiosRequestConfig,
): Promise<InternalAxiosRequestConfig> {
  await ensureSessionExtended()
  return config
}

export const shopsClient: AxiosInstance = axios.create({
  baseURL: shopsOrigin,
  withCredentials: true,
  timeout: 120_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

shopsClient.interceptors.request.use(shopsRequestInterceptor)

shopsClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config as RetryableConfig | undefined

    if (isUnauthorizedError(error) && !skipSessionExtend && config && !config._authRetried) {
      config._authRetried = true
      try {
        await extendSession()
        return shopsClient.request(config)
      } catch (authError) {
        return Promise.reject(authError)
      }
    }
    return Promise.reject(error)
  },
)

export async function fetchShops(params: ShopSearchParams = {}): Promise<ShopListResponse> {
  const { data } = await shopsClient.get<ShopListResponse>('/shops', { params })
  return data
}

export async function fetchShop(shopId: number): Promise<ShopDetailResponse> {
  const { data } = await shopsClient.get<ShopDetailResponse>(`/shops/${shopId}`)
  return data
}

export async function createShop(body: ShopWriteInput): Promise<ShopDetailResponse> {
  const { data } = await shopsClient.post<ShopDetailResponse>('/shops', body)
  return data
}

export async function updateShop(
  shopId: number,
  body: ShopWriteInput,
): Promise<ShopDetailResponse> {
  const { data } = await shopsClient.put<ShopDetailResponse>(`/shops/${shopId}`, body)
  return data
}

export async function deleteShop(shopId: number): Promise<void> {
  await shopsClient.delete(`/shops/${shopId}`)
}

export async function fetchGenres(includeUsageCount = false): Promise<Genre[]> {
  const { data } = await shopsClient.get<GenreListResponse>('/genres', {
    params: { include_usage_count: includeUsageCount },
  })
  return data.items
}

export async function fetchImageBlob(url: string): Promise<Blob> {
  const { data } = await shopsClient.get<Blob>(url, { responseType: 'blob' })
  return data
}

export async function createGenre(name: string, sort_order = 0): Promise<Genre> {
  const { data } = await shopsClient.post<{ genre: Genre }>('/genres', { name, sort_order })
  return data.genre
}
