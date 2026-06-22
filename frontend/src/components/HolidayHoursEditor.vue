<script setup lang="ts">
import type { HolidayHoursInput, OpeningSlotInput } from '../api/types'

const holidayHours = defineModel<HolidayHoursInput | null>({ required: true })

function getHours(): HolidayHoursInput {
  return holidayHours.value ?? { is_closed: false, memo: '', slots: [] }
}

function update(patch: Partial<HolidayHoursInput>): void {
  holidayHours.value = { ...getHours(), ...patch }
}

function toggleClosed(closed: boolean): void {
  update({ is_closed: closed })
}

function addSlot(): void {
  const hours = getHours()
  const slots: OpeningSlotInput[] = [
    ...hours.slots,
    { open_time: '11:00', close_time: '14:00', sort_order: hours.slots.length },
  ]
  update({ slots, is_closed: false })
}

function removeSlot(index: number): void {
  const hours = getHours()
  const slots = hours.slots
    .filter((_, i) => i !== index)
    .map((slot, i) => ({ ...slot, sort_order: i }))
  update({ slots })
}

function patchSlot(index: number, patch: Partial<OpeningSlotInput>): void {
  const hours = getHours()
  const slots = hours.slots.map((slot, i) => (i === index ? { ...slot, ...patch } : slot))
  update({ slots })
}

function clearAll(): void {
  holidayHours.value = null
}

function hasContent(): boolean {
  const hours = getHours()
  return (
    hours.is_closed === true ||
    hours.slots.length > 0 ||
    (hours.memo?.trim() ?? '') !== ''
  )
}
</script>

<template>
  <section class="opening-hours holiday-hours">
    <div class="section-head">
      <h3>祝日の営業時間</h3>
      <button v-if="hasContent()" type="button" class="btn small" @click="clearAll">
        設定をクリア
      </button>
    </div>
    <p class="hint">曜日とは別に、祝日の営業時間を設定できます。</p>

    <div class="day-row">
      <div class="day-label">祝日</div>

      <div class="day-content">
        <label class="closed-flag">
          <input
            type="checkbox"
            :checked="getHours().is_closed === true"
            @change="toggleClosed(($event.target as HTMLInputElement).checked)"
          />
          定休日
        </label>

        <template v-if="getHours().is_closed">
          <p class="closed-note">祝日は定休日として登録されます</p>
        </template>

        <template v-else-if="getHours().slots.length === 0">
          <div class="day-actions">
            <button type="button" class="btn small" @click="addSlot">時間帯を追加</button>
          </div>
        </template>

        <template v-else>
          <div v-for="(slot, idx) in getHours().slots" :key="idx" class="slot-line">
            <input
              type="time"
              class="time-input"
              aria-label="開始"
              :value="slot.open_time"
              @input="patchSlot(idx, { open_time: ($event.target as HTMLInputElement).value })"
            />
            <span class="slot-sep">～</span>
            <input
              type="time"
              class="time-input"
              aria-label="終了"
              :value="slot.close_time"
              @input="patchSlot(idx, { close_time: ($event.target as HTMLInputElement).value })"
            />
            <button type="button" class="btn small" @click="removeSlot(idx)">削除</button>
          </div>

          <div class="day-actions">
            <button type="button" class="btn small" @click="addSlot">時間帯を追加</button>
          </div>
        </template>

        <label class="day-memo">
          <span class="day-memo-label">補足メモ</span>
          <input
            type="text"
            :value="getHours().memo ?? ''"
            placeholder="祝日前日は短縮営業 など"
            @input="update({ memo: ($event.target as HTMLInputElement).value })"
          />
        </label>
      </div>
    </div>
  </section>
</template>
