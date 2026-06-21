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

function commitDays(nextDays: OpeningDayInput[]): void {
  days.value = nextDays
    .filter((d) => d.slots.length > 0 || (d.day_memo?.trim() ?? '') !== '')
    .sort((a, b) => a.day_of_week - b.day_of_week)
}

function updateDay(dow: number, patch: Partial<OpeningDayInput>): void {
  const current = getDay(dow)
  const next = { ...current, ...patch, day_of_week: dow }
  const others = days.value.filter((d) => d.day_of_week !== dow)
  commitDays([...others, next])
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
  const slots = day.slots
    .filter((_, i) => i !== index)
    .map((slot, i) => ({ ...slot, sort_order: i }))
  updateDay(dow, { slots })
}

function patchSlot(dow: number, index: number, patch: Partial<OpeningSlotInput>): void {
  const day = getDay(dow)
  const slots = day.slots.map((slot, i) => (i === index ? { ...slot, ...patch } : slot))
  updateDay(dow, { slots })
}

function copyToOtherDays(sourceDow: number): void {
  const source = getDay(sourceDow)
  if (source.slots.length === 0) {
    return
  }
  const label = DAY_LABELS[sourceDow]
  if (
    !window.confirm(`${label}曜の営業時間を、他のすべての曜日にコピーしますか？\n（既存の設定は上書きされます）`)
  ) {
    return
  }

  const slotsCopy = source.slots.map((slot, index) => ({
    open_time: slot.open_time,
    close_time: slot.close_time,
    sort_order: index,
  }))
  const memoCopy = source.day_memo ?? ''

  const nextDays: OpeningDayInput[] = []
  for (let dow = 0; dow < 7; dow += 1) {
    if (dow === sourceDow) {
      nextDays.push({ ...source, day_of_week: dow })
    } else {
      nextDays.push({
        day_of_week: dow,
        day_memo: memoCopy,
        slots: slotsCopy.map((slot) => ({ ...slot })),
      })
    }
  }
  commitDays(nextDays)
}
</script>

<template>
  <section class="opening-hours">
    <h3>営業時間</h3>

    <div v-for="dow in 7" :key="dow - 1" class="day-row">
      <div class="day-label">{{ DAY_LABELS[dow - 1] }}曜</div>

      <div class="day-content">
        <template v-if="getDay(dow - 1).slots.length === 0">
          <div class="day-actions">
            <button type="button" class="btn small" @click="addSlot(dow - 1)">時間帯を追加</button>
          </div>
        </template>

        <template v-else>
          <div
            v-for="(slot, idx) in getDay(dow - 1).slots"
            :key="idx"
            class="slot-line"
          >
            <input
              type="time"
              class="time-input"
              aria-label="開始"
              :value="slot.open_time"
              @input="patchSlot(dow - 1, idx, { open_time: ($event.target as HTMLInputElement).value })"
            />
            <span class="slot-sep">～</span>
            <input
              type="time"
              class="time-input"
              aria-label="終了"
              :value="slot.close_time"
              @input="patchSlot(dow - 1, idx, { close_time: ($event.target as HTMLInputElement).value })"
            />
            <button type="button" class="btn small" @click="removeSlot(dow - 1, idx)">削除</button>
          </div>

          <div class="day-actions">
            <button type="button" class="btn small" @click="addSlot(dow - 1)">時間帯を追加</button>
            <button type="button" class="btn small" @click="copyToOtherDays(dow - 1)">
              他曜日にコピー
            </button>
          </div>
        </template>

        <label class="day-memo">
          <span class="day-memo-label">補足メモ</span>
          <input
            type="text"
            :value="getDay(dow - 1).day_memo ?? ''"
            placeholder="定休など"
            @input="updateDay(dow - 1, { day_memo: ($event.target as HTMLInputElement).value })"
          />
        </label>
      </div>
    </div>
  </section>
</template>
