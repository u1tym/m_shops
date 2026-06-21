<script setup lang="ts">
import { computed } from 'vue'

import type { OpeningDayInput, OpeningSlotInput } from '../api/types'
import { DAY_LABELS } from '../utils/helpers'

const days = defineModel<OpeningDayInput[]>({ required: true })

const dayMap = computed(() => {
  const map = new Map<number, OpeningDayInput>()
  for (const day of days.value) {
    map.set(day.day_of_week, day)
  }
  return map
})

function getDay(dow: number): OpeningDayInput {
  return (
    dayMap.value.get(dow) ?? {
      day_of_week: dow,
      day_memo: '',
      slots: [],
    }
  )
}

function updateDay(dow: number, patch: Partial<OpeningDayInput>): void {
  const current = getDay(dow)
  const next = { ...current, ...patch, day_of_week: dow }
  const others = days.value.filter((d) => d.day_of_week !== dow)
  const hasContent = (next.day_memo?.trim() ?? '') !== '' || next.slots.length > 0
  days.value = hasContent ? [...others, next].sort((a, b) => a.day_of_week - b.day_of_week) : others
}

function addSlot(dow: number): void {
  const day = getDay(dow)
  const slots: OpeningSlotInput[] = [
    ...day.slots,
    { open_time: '11:00', close_time: '14:00', sort_order: day.slots.length },
  ]
  updateDay(dow, { slots })
}

function removeSlot(dow: number, index: number): void {
  const day = getDay(dow)
  updateDay(dow, { slots: day.slots.filter((_, i) => i !== index) })
}

function patchSlot(dow: number, index: number, patch: Partial<OpeningSlotInput>): void {
  const day = getDay(dow)
  const slots = day.slots.map((slot, i) => (i === index ? { ...slot, ...patch } : slot))
  updateDay(dow, { slots })
}
</script>

<template>
  <section class="opening-hours">
    <h3>営業時間</h3>
    <div v-for="dow in 7" :key="dow - 1" class="day-block">
      <div class="day-head">
        <strong>{{ DAY_LABELS[dow - 1] }}曜</strong>
      </div>
      <label>
        補足メモ
        <input
          type="text"
          :value="getDay(dow - 1).day_memo ?? ''"
          placeholder="定休など"
          @input="updateDay(dow - 1, { day_memo: ($event.target as HTMLInputElement).value })"
        />
      </label>
      <div v-for="(slot, idx) in getDay(dow - 1).slots" :key="idx" class="slot-row">
        <input
          type="time"
          :value="slot.open_time"
          @input="patchSlot(dow - 1, idx, { open_time: ($event.target as HTMLInputElement).value })"
        />
        <span>〜</span>
        <input
          type="time"
          :value="slot.close_time"
          @input="patchSlot(dow - 1, idx, { close_time: ($event.target as HTMLInputElement).value })"
        />
        <button type="button" class="btn small" @click="removeSlot(dow - 1, idx)">削除</button>
      </div>
      <button type="button" class="btn small" @click="addSlot(dow - 1)">時間帯を追加</button>
    </div>
  </section>
</template>
