<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getErrorMessage } from '../api/auth'
import {
  createShop,
  deleteShop,
  fetchGenres,
  fetchImageBlob,
  fetchShop,
  updateShop,
} from '../api/shopsClient'
import type {
  FormImageItem,
  Genre,
  HolidayHoursInput,
  KeywordInput,
  MenuInput,
  OpeningDayInput,
  ShopWriteInput,
  StationInput,
  VisitInput,
} from '../api/types'
import AppHeader from '../components/AppHeader.vue'
import HolidayHoursEditor from '../components/HolidayHoursEditor.vue'
import ImagePasteArea from '../components/ImagePasteArea.vue'
import OpeningHoursEditor from '../components/OpeningHoursEditor.vue'
import VisitDatesEditor from '../components/VisitDatesEditor.vue'
import { blobToDataUrl, newKey } from '../utils/helpers'
import { PREFECTURES } from '../utils/prefectures'
import { resolveShopImagePath } from '../utils/imageUrl'

const props = defineProps<{
  id?: string
}>()

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => route.name === 'edit' && !!props.id)
const shopId = computed(() => (props.id ? Number(props.id) : null))

const genres = ref<Genre[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)

const name = ref('')
const prefecture = ref('')
const address = ref('')
const scheduleMemo = ref('')
const lastVerifiedOn = ref('')
const memo = ref('')
const genreIds = ref<number[]>([])
const openingDays = ref<OpeningDayInput[]>([])
const holidayHours = ref<HolidayHoursInput | null>(null)
const menus = ref<MenuInput[]>([])
const keywords = ref<KeywordInput[]>([])
const stations = ref<StationInput[]>([])
const visits = ref<VisitInput[]>([])
const images = ref<FormImageItem[]>([])

function emptyMenu(): MenuInput {
  return { menu_name: '', memo: '', sort_order: menus.value.length }
}

function emptyKeyword(): KeywordInput {
  return { keyword: '', sort_order: keywords.value.length }
}

function emptyStation(): StationInput {
  return {
    transport_line: '電車',
    station_name: '',
    walk_minutes: null,
    distance_memo: '',
    sort_order: stations.value.length,
  }
}

async function loadGenres(): Promise<void> {
  genres.value = await fetchGenres()
}

async function loadShop(): Promise<void> {
  if (!shopId.value) {
    return
  }
  loading.value = true
  error.value = null
  try {
    const { shop } = await fetchShop(shopId.value)
    name.value = shop.name
    prefecture.value = shop.prefecture ?? ''
    address.value = shop.address ?? ''
    scheduleMemo.value = shop.schedule_memo ?? ''
    lastVerifiedOn.value = shop.last_verified_on ?? ''
    memo.value = shop.memo ?? ''
    genreIds.value = shop.genres.map((g) => g.id)
    openingDays.value = shop.opening_days.map((d) => ({
      day_of_week: d.day_of_week,
      day_memo: d.day_memo,
      is_closed: d.is_closed,
      slots: d.slots.map((s) => ({ ...s })),
    }))
    holidayHours.value = shop.holiday_hours
      ? {
          is_closed: shop.holiday_hours.is_closed,
          memo: shop.holiday_hours.memo,
          slots: shop.holiday_hours.slots.map((s) => ({ ...s })),
        }
      : null
    menus.value = shop.menus.map((m) => ({ ...m }))
    keywords.value = shop.keywords.map((k) => ({ ...k }))
    stations.value = shop.stations.map((s) => ({ ...s }))
    visits.value = shop.visits.map((v) => ({ ...v }))

    const loadedImages: FormImageItem[] = []
    for (const meta of shop.images) {
      const blob = await fetchImageBlob(resolveShopImagePath(meta.url))
      const dataUrl = await blobToDataUrl(blob)
      loadedImages.push({
        key: newKey(),
        id: meta.id,
        file_name: meta.file_name,
        mime_type: meta.mime_type,
        previewUrl: dataUrl,
        sort_order: meta.sort_order,
      })
    }
    images.value = loadedImages
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

function toggleGenre(id: number, checked: boolean): void {
  if (checked) {
    if (!genreIds.value.includes(id)) {
      genreIds.value = [...genreIds.value, id]
    }
  } else {
    genreIds.value = genreIds.value.filter((gid) => gid !== id)
  }
}

function setTodayVerified(): void {
  const today = new Date()
  const y = today.getFullYear()
  const m = String(today.getMonth() + 1).padStart(2, '0')
  const d = String(today.getDate()).padStart(2, '0')
  lastVerifiedOn.value = `${y}-${m}-${d}`
}

function buildHolidayHoursPayload(): HolidayHoursInput | null {
  if (!holidayHours.value) {
    return null
  }
  const hours = holidayHours.value
  const hasContent =
    hours.is_closed === true ||
    hours.slots.length > 0 ||
    (hours.memo?.trim() ?? '') !== ''
  if (!hasContent) {
    return null
  }
  return {
    is_closed: hours.is_closed ?? false,
    memo: hours.memo?.trim() || null,
    slots: hours.slots.map((s, index) => ({
      open_time: s.open_time,
      close_time: s.close_time,
      sort_order: index,
    })),
  }
}

function buildPayload(): ShopWriteInput {
  return {
    name: name.value.trim(),
    prefecture: prefecture.value || null,
    address: address.value.trim() || null,
    schedule_memo: scheduleMemo.value.trim() || null,
    last_verified_on: lastVerifiedOn.value || null,
    memo: memo.value.trim() || null,
    genre_ids: [...genreIds.value],
    opening_days: openingDays.value.map((d) => ({
      day_of_week: d.day_of_week,
      day_memo: d.day_memo?.trim() || null,
      is_closed: d.is_closed ?? false,
      slots: d.slots.map((s, index) => ({
        open_time: s.open_time,
        close_time: s.close_time,
        sort_order: index,
      })),
    })),
    holiday_hours: buildHolidayHoursPayload(),
    menus: menus.value
      .filter((m) => m.menu_name.trim())
      .map((m, index) => ({
        id: m.id,
        menu_name: m.menu_name.trim(),
        memo: m.memo?.trim() || null,
        sort_order: index,
      })),
    keywords: keywords.value
      .filter((k) => k.keyword.trim())
      .map((k, index) => ({
        id: k.id,
        keyword: k.keyword.trim(),
        sort_order: index,
      })),
    stations: stations.value
      .filter((s) => s.station_name.trim())
      .map((s, index) => ({
        id: s.id,
        transport_line: s.transport_line.trim(),
        station_name: s.station_name.trim(),
        walk_minutes: s.walk_minutes,
        distance_memo: s.distance_memo?.trim() || null,
        sort_order: index,
      })),
    visits: visits.value
      .filter((v) => v.visit_date)
      .map((v) => ({
        id: v.id,
        visit_date: v.visit_date,
        memo: v.memo?.trim() || null,
      })),
    images: images.value.map((img, index) => ({
      id: img.id,
      file_name: img.file_name,
      mime_type: img.mime_type,
      data_base64: img.data_base64,
      sort_order: index,
    })),
  }
}

async function onSubmit(): Promise<void> {
  if (!name.value.trim()) {
    error.value = '店名を入力してください'
    return
  }
  saving.value = true
  error.value = null
  try {
    const payload = buildPayload()
    if (isEdit.value && shopId.value) {
      await updateShop(shopId.value, payload)
    } else {
      await createShop(payload)
    }
    await router.push({ name: 'list' })
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function onDelete(): Promise<void> {
  if (!isEdit.value || !shopId.value) {
    return
  }
  if (!window.confirm('この店舗を削除しますか？')) {
    return
  }
  saving.value = true
  error.value = null
  try {
    await deleteShop(shopId.value)
    await router.push({ name: 'list' })
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadGenres()
  if (isEdit.value) {
    await loadShop()
  }
})
</script>

<template>
  <div class="page">
    <AppHeader :title="isEdit ? '店舗編集' : '店舗追加'">
      <template #actions>
        <button type="button" class="btn small" @click="router.push({ name: 'list' })">一覧</button>
      </template>
    </AppHeader>

    <main class="page-body">
      <p v-if="loading" class="status">読み込み中…</p>
      <form v-else class="shop-form" @submit.prevent="onSubmit">
        <section>
          <h3>基本情報</h3>
          <label>
            店名 <span class="req">*</span>
            <input v-model="name" type="text" required maxlength="200" />
          </label>
          <label>
            都道府県
            <select v-model="prefecture">
              <option value="">未選択</option>
              <option v-for="p in PREFECTURES" :key="p" :value="p">{{ p }}</option>
            </select>
          </label>
          <label>
            住所
            <input v-model="address" type="text" />
          </label>
          <label>
            最終確認日
            <div class="date-input-row">
              <input v-model="lastVerifiedOn" type="date" />
              <button type="button" class="btn small" @click="setTodayVerified">今日</button>
            </div>
          </label>
          <label>
            営業メモ（祝日など）
            <textarea v-model="scheduleMemo" rows="2" />
          </label>
          <label>
            メモ
            <textarea v-model="memo" rows="3" />
          </label>
        </section>

        <section>
          <div class="section-head">
            <h3>ジャンル</h3>
            <button type="button" class="btn small" @click="router.push({ name: 'genres' })">
              ジャンル管理
            </button>
          </div>
          <p v-if="genres.length === 0" class="hint">
            ジャンルがありません。「ジャンル管理」から追加してください。
          </p>
          <div class="genre-checkboxes">
            <label v-for="g in genres" :key="g.id" class="checkbox-label">
              <input
                type="checkbox"
                :checked="genreIds.includes(g.id)"
                @change="toggleGenre(g.id, ($event.target as HTMLInputElement).checked)"
              />
              {{ g.name }}
            </label>
          </div>
        </section>

        <OpeningHoursEditor v-model="openingDays" />

        <HolidayHoursEditor v-model="holidayHours" />

        <VisitDatesEditor v-model="visits" />

        <section>
          <h3>頼みたいメニュー</h3>
          <div v-for="(menu, index) in menus" :key="index" class="repeat-row">
            <input v-model="menu.menu_name" type="text" placeholder="メニュー名" />
            <input v-model="menu.memo" type="text" placeholder="メモ" />
            <button type="button" class="btn small" @click="menus.splice(index, 1)">削除</button>
          </div>
          <button type="button" class="btn small" @click="menus.push(emptyMenu())">追加</button>
        </section>

        <section>
          <h3>キーワード</h3>
          <div v-for="(kw, index) in keywords" :key="index" class="repeat-row">
            <input v-model="kw.keyword" type="text" placeholder="キーワード" />
            <button type="button" class="btn small" @click="keywords.splice(index, 1)">削除</button>
          </div>
          <button type="button" class="btn small" @click="keywords.push(emptyKeyword())">追加</button>
        </section>

        <section>
          <h3>最寄り駅</h3>
          <div v-for="(st, index) in stations" :key="index" class="station-row">
            <input v-model="st.transport_line" type="text" placeholder="交通機関・路線（例: 電車 JR山手線）" />
            <input v-model="st.station_name" type="text" placeholder="駅名" />
            <input v-model.number="st.walk_minutes" type="number" min="0" placeholder="徒歩(分)" />
            <input v-model="st.distance_memo" type="text" placeholder="距離メモ" />
            <button type="button" class="btn small" @click="stations.splice(index, 1)">削除</button>
          </div>
          <button type="button" class="btn small" @click="stations.push(emptyStation())">追加</button>
        </section>

        <ImagePasteArea v-model="images" />

        <p v-if="error" class="error">{{ error }}</p>

        <div class="form-actions">
          <button type="submit" class="btn primary" :disabled="saving">
            {{ saving ? '保存中…' : '保存' }}
          </button>
          <button
            v-if="isEdit"
            type="button"
            class="btn danger"
            :disabled="saving"
            @click="onDelete"
          >
            削除
          </button>
        </div>
      </form>
    </main>
  </div>
</template>
