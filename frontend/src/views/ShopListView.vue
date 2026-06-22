<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { getErrorMessage } from '../api/auth'
import { fetchGenres, fetchShops } from '../api/shopsClient'
import type { Genre, ShopSummary } from '../api/types'
import AppHeader from '../components/AppHeader.vue'
import ShopCard from '../components/ShopCard.vue'
import { DAY_LABELS } from '../utils/helpers'

const router = useRouter()

const query = ref('')
const genreId = ref<number | undefined>(undefined)
const openDayOfWeek = ref<number | undefined>(undefined)
const openTime = ref('')
const hasImage = ref<'yes' | 'no'>('no')
const genres = ref<Genre[]>([])
const shops = ref<ShopSummary[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const hasActiveFilters = (): boolean => {
  return (
    query.value.trim() !== '' ||
    genreId.value !== undefined ||
    (openDayOfWeek.value !== undefined && openTime.value !== '')
  )
}

async function loadGenres(): Promise<void> {
  genres.value = await fetchGenres()
}

async function loadShops(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const trimmed = query.value.trim()
    const params: Parameters<typeof fetchShops>[0] = {
      page: 1,
      per_page: 100,
    }
    if (trimmed) {
      params.search = trimmed
    }
    if (genreId.value !== undefined) {
      params.genre_id = genreId.value
    }
    if (openDayOfWeek.value !== undefined && openTime.value) {
      params.open_day_of_week = openDayOfWeek.value
      params.open_time = openTime.value
    }
    if (hasImage.value === 'yes') {
      params.has_image = true
    }
    const data = await fetchShops(params)
    shops.value = data.items
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function goDetail(id: number): void {
  router.push({ name: 'detail', params: { id } })
}

function goCreate(): void {
  router.push({ name: 'create' })
}

watch([query, genreId, openDayOfWeek, openTime, hasImage], () => {
  void loadShops()
})

onMounted(async () => {
  await loadGenres()
  await loadShops()
})
</script>

<template>
  <div class="page">
    <AppHeader title="お店一覧">
      <template #actions>
        <button type="button" class="btn small primary" @click="goCreate">新規追加</button>
      </template>
    </AppHeader>

    <main class="page-body">
      <section class="list-search">
        <label class="list-search-label">
          検索
          <input
            v-model="query"
            type="search"
            placeholder="店名・キーワード"
          />
        </label>
        <div class="list-search-filters">
          <select
            class="inline-control"
            :value="genreId ?? ''"
            @change="
              genreId = ($event.target as HTMLSelectElement).value
                ? Number(($event.target as HTMLSelectElement).value)
                : undefined
            "
          >
            <option value="">すべて</option>
            <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
          <span class="opening-hours-filter">
            <span class="filter-prefix">営業日</span>
            <select
              class="inline-control"
              :value="openDayOfWeek ?? ''"
              @change="
                openDayOfWeek = ($event.target as HTMLSelectElement).value
                  ? Number(($event.target as HTMLSelectElement).value)
                  : undefined
              "
            >
              <option value="">曜日指定</option>
              <option v-for="(label, dow) in DAY_LABELS" :key="dow" :value="dow">
                {{ label }}曜
              </option>
            </select>
            <input
              v-model="openTime"
              class="inline-control"
              type="time"
              title="時刻指定"
            />
          </span>
          <select v-model="hasImage" class="inline-control" title="参考画像の表示">
            <option value="no">参考画像: 非表示</option>
            <option value="yes">参考画像: 表示</option>
          </select>
        </div>
      </section>

      <p v-if="loading" class="status">読み込み中…</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <p v-else-if="shops.length === 0" class="hint">
        {{ hasActiveFilters() ? '該当する店舗がありません。' : '店舗がありません。' }}
      </p>

      <div class="shop-list">
        <ShopCard
          v-for="shop in shops"
          :key="shop.id"
          :shop="shop"
          clickable
          @click="goDetail(shop.id)"
        />
      </div>
    </main>
  </div>
</template>
