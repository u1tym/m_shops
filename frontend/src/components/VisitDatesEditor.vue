<script setup lang="ts">
import { computed } from 'vue'

import type { VisitInput } from '../api/types'

const visits = defineModel<VisitInput[]>({ required: true })

const sortedVisits = computed(() =>
  [...visits.value].sort((a, b) => b.visit_date.localeCompare(a.visit_date)),
)

function emptyVisit(): VisitInput {
  return { visit_date: '', memo: '' }
}

function addVisit(): void {
  visits.value = [...visits.value, emptyVisit()]
}

function removeVisit(index: number): void {
  visits.value = visits.value.filter((_, i) => i !== index)
}

function updateVisit(index: number, patch: Partial<VisitInput>): void {
  visits.value = visits.value.map((v, i) => (i === index ? { ...v, ...patch } : v))
}

function setToday(index: number): void {
  const today = new Date()
  const y = today.getFullYear()
  const m = String(today.getMonth() + 1).padStart(2, '0')
  const d = String(today.getDate()).padStart(2, '0')
  updateVisit(index, { visit_date: `${y}-${m}-${d}` })
}
</script>

<template>
  <section>
    <h3>来店日</h3>
    <p class="hint">複数登録できます。一覧・詳細では最新の来店日を表示します。</p>

    <div v-for="(visit, index) in visits" :key="index" class="repeat-row visit-row">
      <input
        type="date"
        :value="visit.visit_date"
        @input="updateVisit(index, { visit_date: ($event.target as HTMLInputElement).value })"
      />
      <button type="button" class="btn small" @click="setToday(index)">今日</button>
      <input
        type="text"
        :value="visit.memo ?? ''"
        placeholder="メモ"
        @input="updateVisit(index, { memo: ($event.target as HTMLInputElement).value })"
      />
      <button type="button" class="btn small" @click="removeVisit(index)">削除</button>
    </div>

    <button type="button" class="btn small" @click="addVisit">来店日を追加</button>

    <div v-if="sortedVisits.length > 0" class="visit-preview">
      <p class="hint">
        最終来店日: {{ sortedVisits[0].visit_date }}
        <span v-if="sortedVisits.length > 1">（他 {{ sortedVisits.length - 1 }} 件）</span>
      </p>
    </div>
  </section>
</template>
