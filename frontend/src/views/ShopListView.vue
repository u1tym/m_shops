<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { getErrorMessage } from '../api/auth'
import { fetchGenres, fetchShops } from '../api/shopsClient'
import type { Genre, ShopSearchParams, ShopSummary } from '../api/types'
import AppHeader from '../components/AppHeader.vue'
import ShopCard from '../components/ShopCard.vue'
import ShopSearchForm from '../components/ShopSearchForm.vue'

const router = useRouter()

const genres = ref<Genre[]>([])
const shops = ref<ShopSummary[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref<string | null>(null)

const search = ref<ShopSearchParams>({
  station: '',
  location: '',
  keyword: '',
  genre_id: undefined,
  q: '',
  page: 1,
  per_page: 20,
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
    }
    const data = await fetchShops(params)
    shops.value = data.items
    total.value = data.total
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function onSearch(): void {
  search.value.page = 1
  void loadShops()
}

function goMap(): void {
  router.push({ name: 'map', query: buildQuery() })
}

function goCreate(): void {
  router.push({ name: 'create' })
}

function goEdit(id: number): void {
  router.push({ name: 'edit', params: { id } })
}

function buildQuery(): Record<string, string> {
  const q: Record<string, string> = {}
  if (search.value.station?.trim()) q.station = search.value.station.trim()
  if (search.value.location?.trim()) q.location = search.value.location.trim()
  if (search.value.keyword?.trim()) q.keyword = search.value.keyword.trim()
  if (search.value.q?.trim()) q.q = search.value.q.trim()
  if (search.value.genre_id) q.genre_id = String(search.value.genre_id)
  return q
}

onMounted(async () => {
  await loadGenres()
  await loadShops()
})
</script>

<template>
  <div class="page">
    <AppHeader title="お店一覧">
      <template #actions>
        <button type="button" class="btn small" @click="goMap">地図</button>
        <button type="button" class="btn small primary" @click="goCreate">追加</button>
      </template>
    </AppHeader>

    <main class="page-body">
      <ShopSearchForm v-model="search" :genres="genres" @search="onSearch" />

      <p v-if="loading" class="status">読み込み中…</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <p v-else class="status">{{ total }} 件</p>

      <div class="shop-list">
        <ShopCard v-for="shop in shops" :key="shop.id" :shop="shop">
          <template #actions>
            <button type="button" class="btn small" @click="goEdit(shop.id)">編集</button>
            <a
              v-if="shop.google_maps_url"
              :href="shop.google_maps_url"
              class="btn small"
              target="_blank"
              rel="noopener noreferrer"
            >
              地図
            </a>
          </template>
        </ShopCard>
      </div>
    </main>
  </div>
</template>
