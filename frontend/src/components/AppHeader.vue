<script setup lang="ts">
import { menuPageUrl } from '../config'

withDefaults(
  defineProps<{
    title: string
    showBack?: boolean
  }>(),
  { showBack: true },
)

function goMenu(): void {
  window.location.assign(menuPageUrl)
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <button
        v-if="showBack"
        type="button"
        class="btn-back"
        aria-label="メニューに戻る"
        @click="goMenu"
      >
        ← 戻る
      </button>
    </div>
    <h1 class="header-title">{{ title }}</h1>
    <div class="header-right">
      <slot name="actions" />
    </div>
  </header>
</template>
