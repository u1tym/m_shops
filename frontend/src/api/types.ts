export interface GenreRef {
  id: number
  name: string
  sort_order: number
}

export interface Genre extends GenreRef {
  created_at: string
  updated_at: string
  shop_count?: number
}

export interface StationSummary {
  id: number
  station_name: string
  transport_type: string
  walk_minutes: number | null
  sort_order: number
}

export interface Station extends StationSummary {
  line_name: string | null
  distance_memo: string | null
}

export interface OpeningSlot {
  open_time: string
  close_time: string
  sort_order: number
}

export interface OpeningDay {
  day_of_week: number
  day_memo: string | null
  slots: OpeningSlot[]
}

export interface Menu {
  id: number
  menu_name: string
  memo: string | null
  sort_order: number
}

export interface Keyword {
  id: number
  keyword: string
  sort_order: number
}

export interface ImageMeta {
  id: number
  file_name: string | null
  mime_type: string
  file_size_bytes: number
  sort_order: number
  url: string
}

export interface ShopSummary {
  id: number
  name: string
  address: string | null
  google_maps_url: string | null
  schedule_memo: string | null
  last_verified_on: string | null
  memo: string | null
  genres: GenreRef[]
  stations: StationSummary[]
  created_at: string
  updated_at: string
}

export interface ShopDetail extends ShopSummary {
  opening_days: OpeningDay[]
  menus: Menu[]
  keywords: Keyword[]
  stations: Station[]
  images: ImageMeta[]
}

export interface ShopListResponse {
  items: ShopSummary[]
  total: number
  page: number
  per_page: number
}

export interface ShopDetailResponse {
  shop: ShopDetail
}

export interface GenreListResponse {
  items: Genre[]
}

export interface ShopSearchParams {
  station?: string
  location?: string
  keyword?: string
  genre_id?: number
  q?: string
  page?: number
  per_page?: number
}

export interface OpeningSlotInput {
  open_time: string
  close_time: string
  sort_order: number
}

export interface OpeningDayInput {
  day_of_week: number
  day_memo?: string | null
  slots: OpeningSlotInput[]
}

export interface MenuInput {
  id?: number
  menu_name: string
  memo?: string | null
  sort_order?: number
}

export interface KeywordInput {
  id?: number
  keyword: string
  sort_order?: number
}

export interface StationInput {
  id?: number
  transport_type: string
  line_name?: string | null
  station_name: string
  walk_minutes?: number | null
  distance_memo?: string | null
  sort_order?: number
}

export interface ImageInput {
  id?: number
  file_name?: string | null
  mime_type: string
  data_base64?: string
  sort_order?: number
}

export interface ShopWriteInput {
  name: string
  address?: string | null
  schedule_memo?: string | null
  last_verified_on?: string | null
  memo?: string | null
  genre_ids: number[]
  opening_days: OpeningDayInput[]
  menus: MenuInput[]
  keywords: KeywordInput[]
  stations: StationInput[]
  images: ImageInput[]
}

export interface FormImageItem {
  key: string
  id?: number
  file_name: string | null
  mime_type: string
  previewUrl: string
  data_base64?: string
  sort_order: number
}
