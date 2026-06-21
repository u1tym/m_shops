<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getErrorMessage } from '../api/auth'
import { fetchImageBlob, fetchShop } from '../api/shopsClient'
import type { ShopDetail } from '../api/types'
import AppHeader from '../components/AppHeader.vue'
import { DAY_LABELS } from '../utils/helpers'
import { resolveShopImagePath } from '../utils/imageUrl'

const props = defineProps<{
  id: string
}>()

const route = useRoute()
const router = useRouter()

const shop = ref<ShopDetail | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const imageUrls = ref<string[]>([])

async function loadShop(): Promise<void> {
  loading.value = true
  error.value = null
  revokeImageUrls()
  try {
    const shopId = Number(props.id)
    const { shop: detail } = await fetchShop(shopId)
    shop.value = detail
    const urls: string[] = []
    for (const image of detail.images) {
      const blob = await fetchImageBlob(resolveShopImagePath(image.url))
      urls.push(URL.createObjectURL(blob))
    }
    imageUrls.value = urls
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function revokeImageUrls(): void {
  for (const url of imageUrls.value) {
    URL.revokeObjectURL(url)
  }
  imageUrls.value = []
}

function goEdit(): void {
  router.push({ name: 'edit', params: { id: props.id } })
}

function formatDay(dow: number): string {
  return `${DAY_LABELS[dow]}曜`
}

onMounted(() => {
  void loadShop()
})

onUnmounted(() => {
  revokeImageUrls()
})

watch(
  () => route.params.id,
  () => {
    void loadShop()
  },
)
</script>

<template>
  <div class="page">
    <AppHeader title="店舗詳細">
      <template #actions>
        <button type="button" class="btn small" @click="router.push({ name: 'list' })">一覧</button>
        <button v-if="shop" type="button" class="btn small primary" @click="goEdit">編集</button>
      </template>
    </AppHeader>

    <main class="page-body">
      <p v-if="loading" class="status">読み込み中…</p>
      <p v-else-if="error" class="error">{{ error }}</p>

      <template v-else-if="shop">
        <section class="detail-section">
          <h2 class="detail-name">{{ shop.name }}</h2>
          <div v-if="shop.genres.length" class="genre-tags">
            <span v-for="g in shop.genres" :key="g.id" class="tag">{{ g.name }}</span>
          </div>
        </section>

        <section v-if="shop.address" class="detail-section">
          <h3>住所</h3>
          <p>{{ shop.address }}</p>
          <a
            v-if="shop.google_maps_url"
            :href="shop.google_maps_url"
            class="map-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            Google マップで開く
          </a>
        </section>

        <section v-if="shop.last_verified_on" class="detail-section">
          <h3>最終確認日</h3>
          <p>{{ shop.last_verified_on }}</p>
        </section>

        <section v-if="shop.schedule_memo" class="detail-section">
          <h3>営業メモ</h3>
          <p class="pre-wrap">{{ shop.schedule_memo }}</p>
        </section>

        <section v-if="shop.opening_days.length" class="detail-section">
          <h3>営業時間</h3>
          <div v-for="day in shop.opening_days" :key="day.day_of_week" class="detail-day">
            <strong>{{ formatDay(day.day_of_week) }}</strong>
            <ul v-if="day.slots.length" class="detail-slots">
              <li v-for="(slot, idx) in day.slots" :key="idx">
                {{ slot.open_time }} ～ {{ slot.close_time }}
              </li>
            </ul>
            <p v-else class="hint">定休</p>
            <p v-if="day.day_memo" class="day-memo">{{ day.day_memo }}</p>
          </div>
        </section>

        <section v-if="shop.menus.length" class="detail-section">
          <h3>頼みたいメニュー</h3>
          <ul>
            <li v-for="menu in shop.menus" :key="menu.id">
              {{ menu.menu_name }}
              <span v-if="menu.memo" class="sub">（{{ menu.memo }}）</span>
            </li>
          </ul>
        </section>

        <section v-if="shop.keywords.length" class="detail-section">
          <h3>キーワード</h3>
          <div class="genre-tags">
            <span v-for="kw in shop.keywords" :key="kw.id" class="tag">{{ kw.keyword }}</span>
          </div>
        </section>

        <section v-if="shop.stations.length" class="detail-section">
          <h3>最寄り駅</h3>
          <ul>
            <li v-for="st in shop.stations" :key="st.id">
              {{ st.station_name }}（{{ st.transport_type }}
              <template v-if="st.line_name">・{{ st.line_name }}</template>
              <template v-if="st.walk_minutes != null">・徒歩{{ st.walk_minutes }}分</template>）
              <span v-if="st.distance_memo" class="sub">{{ st.distance_memo }}</span>
            </li>
          </ul>
        </section>

        <section v-if="shop.memo" class="detail-section">
          <h3>メモ</h3>
          <p class="pre-wrap">{{ shop.memo }}</p>
        </section>

        <section v-if="shop.images.length" class="detail-section">
          <h3>参考画像</h3>
          <div class="image-grid">
            <figure v-for="(image, idx) in shop.images" :key="image.id" class="image-item">
              <img :src="imageUrls[idx]" :alt="image.file_name ?? '参考画像'" />
            </figure>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>
