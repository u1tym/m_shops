<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { getErrorMessage } from '../api/auth'
import { createGenre, deleteGenre, fetchGenres, updateGenre } from '../api/shopsClient'
import type { Genre } from '../api/types'
import AppHeader from '../components/AppHeader.vue'

const router = useRouter()

const genres = ref<Genre[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)

const newName = ref('')
const newSortOrder = ref(0)

const editingId = ref<number | null>(null)
const editName = ref('')
const editSortOrder = ref(0)

async function loadGenres(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    genres.value = await fetchGenres(true)
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function onAdd(): Promise<void> {
  const name = newName.value.trim()
  if (!name) {
    error.value = 'ジャンル名を入力してください'
    return
  }
  saving.value = true
  error.value = null
  try {
    await createGenre(name, newSortOrder.value)
    newName.value = ''
    newSortOrder.value = 0
    await loadGenres()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

function startEdit(genre: Genre): void {
  editingId.value = genre.id
  editName.value = genre.name
  editSortOrder.value = genre.sort_order
}

function cancelEdit(): void {
  editingId.value = null
}

async function onSaveEdit(genreId: number): Promise<void> {
  const name = editName.value.trim()
  if (!name) {
    error.value = 'ジャンル名を入力してください'
    return
  }
  saving.value = true
  error.value = null
  try {
    await updateGenre(genreId, { name, sort_order: editSortOrder.value })
    editingId.value = null
    await loadGenres()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function onDelete(genre: Genre): Promise<void> {
  const count = genre.shop_count ?? 0
  const message =
    count > 0
      ? `「${genre.name}」を削除しますか？\n（${count} 件の店舗に紐づいています）`
      : `「${genre.name}」を削除しますか？`
  if (!window.confirm(message)) {
    return
  }
  saving.value = true
  error.value = null
  try {
    await deleteGenre(genre.id)
    if (editingId.value === genre.id) {
      editingId.value = null
    }
    await loadGenres()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  void loadGenres()
})
</script>

<template>
  <div class="page">
    <AppHeader title="ジャンル管理">
      <template #actions>
        <button type="button" class="btn small" @click="router.push({ name: 'list' })">一覧</button>
      </template>
    </AppHeader>

    <main class="page-body">
      <section class="genre-form">
        <h3>ジャンルを追加</h3>
        <form class="add-form" @submit.prevent="onAdd">
          <label>
            名前
            <input v-model="newName" type="text" maxlength="100" placeholder="例: ラーメン" />
          </label>
          <label>
            表示順
            <input v-model.number="newSortOrder" type="number" min="0" />
          </label>
          <button type="submit" class="btn primary" :disabled="saving">追加</button>
        </form>
      </section>

      <p v-if="loading" class="status">読み込み中…</p>
      <p v-if="error" class="error">{{ error }}</p>

      <section v-if="!loading" class="genre-list">
        <h3>登録済みジャンル</h3>
        <p v-if="genres.length === 0" class="hint">ジャンルがありません。</p>
        <article v-for="genre in genres" :key="genre.id" class="genre-item">
          <template v-if="editingId === genre.id">
            <div class="edit-form">
              <label>
                名前
                <input v-model="editName" type="text" maxlength="100" />
              </label>
              <label>
                表示順
                <input v-model.number="editSortOrder" type="number" min="0" />
              </label>
              <div class="item-actions">
                <button type="button" class="btn small primary" :disabled="saving" @click="onSaveEdit(genre.id)">
                  保存
                </button>
                <button type="button" class="btn small" :disabled="saving" @click="cancelEdit">キャンセル</button>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="genre-info">
              <strong>{{ genre.name }}</strong>
              <span class="sub">表示順: {{ genre.sort_order }}</span>
              <span v-if="genre.shop_count != null" class="sub">店舗数: {{ genre.shop_count }}</span>
            </div>
            <div class="item-actions">
              <button type="button" class="btn small" :disabled="saving" @click="startEdit(genre)">編集</button>
              <button type="button" class="btn small danger" :disabled="saving" @click="onDelete(genre)">
                削除
              </button>
            </div>
          </template>
        </article>
      </section>
    </main>
  </div>
</template>
