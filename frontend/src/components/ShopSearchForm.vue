<script setup lang="ts">
import type { Genre, ShopSearchParams } from '../api/types'

const model = defineModel<ShopSearchParams>({ required: true })

defineProps<{
  genres: Genre[]
}>()

const emit = defineEmits<{
  search: []
}>()
</script>

<template>
  <form class="search-form" @submit.prevent="emit('search')">
    <div class="field-row">
      <label>
        駅名
        <input v-model="model.station" type="text" placeholder="例: 渋谷" />
      </label>
      <label>
        場所
        <input v-model="model.location" type="text" placeholder="住所・店名" />
      </label>
    </div>
    <div class="field-row">
      <label>
        キーワード
        <input v-model="model.keyword" type="text" />
      </label>
      <label>
        ジャンル
        <select
          :value="model.genre_id ?? ''"
          @change="model.genre_id = ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined"
        >
          <option value="">すべて</option>
          <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </label>
    </div>
    <label>
      横断検索
      <input v-model="model.q" type="text" placeholder="店名・住所・駅など" />
    </label>
    <p class="hint">横断検索を入力すると、他の条件は無視されます。</p>
    <button type="submit" class="btn primary">検索</button>
  </form>
</template>
