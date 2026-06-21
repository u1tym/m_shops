<script setup lang="ts">
import type { ShopSummary } from '../api/types'

defineProps<{
  shop: ShopSummary
}>()
</script>

<template>
  <article class="shop-card">
    <div class="shop-card-head">
      <h2 class="shop-name">{{ shop.name }}</h2>
      <div v-if="shop.genres.length" class="genre-tags">
        <span v-for="g in shop.genres" :key="g.id" class="tag">{{ g.name }}</span>
      </div>
    </div>
    <p v-if="shop.address" class="shop-address">{{ shop.address }}</p>
    <ul v-if="shop.stations.length" class="station-list">
      <li v-for="st in shop.stations" :key="st.id">
        {{ st.station_name }}（{{ st.transport_type }}
        <template v-if="st.walk_minutes != null">・徒歩{{ st.walk_minutes }}分</template>）
      </li>
    </ul>
    <p v-if="shop.memo" class="shop-memo">{{ shop.memo }}</p>
    <div class="shop-card-actions">
      <slot name="actions" />
    </div>
  </article>
</template>
