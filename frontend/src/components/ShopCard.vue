<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue'

import { fetchImageBlob } from '../api/shopsClient'
import type { ShopSummary } from '../api/types'
import { resolveShopImagePath } from '../utils/imageUrl'

const props = defineProps<{
  shop: ShopSummary
  clickable?: boolean
}>()

const emit = defineEmits<{
  click: []
}>()

const thumbnailUrl = ref<string | null>(null)

async function loadThumbnail(): Promise<void> {
  if (thumbnailUrl.value) {
    URL.revokeObjectURL(thumbnailUrl.value)
    thumbnailUrl.value = null
  }
  const thumb = props.shop.thumbnail
  if (!thumb) {
    return
  }
  try {
    const blob = await fetchImageBlob(resolveShopImagePath(thumb.url))
    thumbnailUrl.value = URL.createObjectURL(blob)
  } catch {
    thumbnailUrl.value = null
  }
}

watch(() => props.shop.thumbnail, () => {
  void loadThumbnail()
}, { immediate: true })

onUnmounted(() => {
  if (thumbnailUrl.value) {
    URL.revokeObjectURL(thumbnailUrl.value)
  }
})
</script>

<template>
  <article
    class="shop-card"
    :class="{ 'shop-card--clickable': clickable, 'shop-card--with-thumb': !!thumbnailUrl }"
    @click="clickable ? emit('click') : undefined"
  >
    <div v-if="thumbnailUrl" class="shop-card-thumb">
      <img :src="thumbnailUrl" :alt="shop.thumbnail?.file_name ?? '参考画像'" />
    </div>

    <div class="shop-card-body">
      <div class="shop-card-head">
        <h2 class="shop-name">{{ shop.name }}</h2>
        <div v-if="shop.genres.length" class="genre-tags">
          <span v-for="g in shop.genres" :key="g.id" class="tag">{{ g.name }}</span>
        </div>
      </div>
      <p v-if="shop.address" class="shop-address">{{ shop.address }}</p>
      <p v-if="shop.last_visit_on" class="shop-last-visit">最終来店: {{ shop.last_visit_on }}</p>
      <ul v-if="shop.stations.length" class="station-list">
        <li v-for="st in shop.stations" :key="st.id">
          {{ st.station_name }}（{{ st.transport_line }}
          <template v-if="st.walk_minutes != null">・徒歩{{ st.walk_minutes }}分</template>）
        </li>
      </ul>
      <p v-if="shop.memo" class="shop-memo">{{ shop.memo }}</p>
      <div v-if="$slots.actions" class="shop-card-actions" @click.stop>
        <slot name="actions" />
      </div>
    </div>
  </article>
</template>
