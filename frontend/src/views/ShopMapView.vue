<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getErrorMessage } from '../api/auth'
import { fetchGenres, fetchShops } from '../api/shopsClient'
import type { Genre, ShopSearchParams, ShopSummary } from '../api/types'
import AppHeader from '../components/AppHeader.vue'
import ShopSearchForm from '../components/ShopSearchForm.vue'
import { mapsEmbedUrl } from '../utils/helpers'

const route = useRoute()
const router = useRouter()

const genres = ref<Genre[]>([])
const shops = ref<ShopSummary[]>([])
const selectedId = ref<number | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const search = ref<ShopSearchParams>({
  station: String(route.query.station ?? ''),
  location: String(route.query.location ?? ''),
  keyword: String(route.query.keyword ?? ''),
  genre_id: route.query.genre_id ? Number(route.query.genre_id) : undefined,
  has_image: route.query.has_image === 'true' ? true : undefined,
  q: String(route.query.q ?? ''),
  page: 1,
  per_page: 100,
})

const selectedShop = computed(() => shops.value.find((s) => s.id === selectedId.value) ?? null)

const embedUrl = computed(() => {
  if (!selectedShop.value?.address) {
    return null
  }
  return mapsEmbedUrl(selectedShop.value.address)
})

async function loadGenres(): Promise<void> {
  genres.value = await fetchGenres()
}

async function loadShops(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const params: ShopSearchParams = {
      page: search.value.page,
      per_page: search.value.per_page,
    }
    if (search.value.q?.trim()) {
      params.q = search.value.q.trim()
    } else {
      if (search.value.station?.trim()) params.station = search.value.station.trim()
      if (search.value.location?.trim()) params.location = search.value.location.trim()
      if (search.value.keyword?.trim()) params.keyword = search.value.keyword.trim()
      if (search.value.genre_id) params.genre_id = search.value.genre_id
      if (search.value.has_image === true) params.has_image = true
    }
    const data = await fetchShops(params)
    shops.value = data.items
    if (data.items.length > 0) {
      const stillExists = data.items.some((s) => s.id === selectedId.value)
      if (!stillExists) {
        selectedId.value = data.items[0].id
      }
    } else {
      selectedId.value = null
    }
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function onSearch(): void {
  router.replace({ query: buildQuery() })
  void loadShops()
}

function buildQuery(): Record<string, string> {
  const q: Record<string, string> = {}
  if (search.value.station?.trim()) q.station = search.value.station.trim()
  if (search.value.location?.trim()) q.location = search.value.location.trim()
  if (search.value.keyword?.trim()) q.keyword = search.value.keyword.trim()
  if (search.value.q?.trim()) q.q = search.value.q.trim()
  if (search.value.genre_id) q.genre_id = String(search.value.genre_id)
  if (search.value.has_image === true) q.has_image = 'true'
  return q
}

watch(selectedId, () => {
  // embed updates via computed
})

onMounted(async () => {
  await loadGenres()
  await loadShops()
})
</script>

<template>
  <div class="page map-page">
    <AppHeader title="地図表示">
      <template #actions>
        <button type="button" class="btn small" @click="router.push({ name: 'list' })">一覧</button>
      </template>
    </AppHeader>

    <main class="page-body">
      <ShopSearchForm v-model="search" :genres="genres" @search="onSearch" />

      <p v-if="loading" class="status">読み込み中…</p>
      <p v-else-if="error" class="error">{{ error }}</p>

      <div class="map-layout">
        <div class="map-panel">
          <iframe
            v-if="embedUrl"
            :src="embedUrl"
            class="map-iframe"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            title="地図"
          />
          <p v-else class="hint">住所がある店舗を選択すると地図を表示します。</p>
        </div>

        <div class="map-shop-list">
          <button
            v-for="shop in shops"
            :key="shop.id"
            type="button"
            class="map-shop-item"
            :class="{ active: shop.id === selectedId }"
            @click="selectedId = shop.id"
          >
            <strong>{{ shop.name }}</strong>
            <span v-if="shop.address" class="sub">{{ shop.address }}</span>
            <a
              v-if="shop.google_maps_url"
              :href="shop.google_maps_url"
              class="map-link"
              target="_blank"
              rel="noopener noreferrer"
              @click.stop
            >
              Google マップで開く
            </a>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>
