<script setup lang="ts">
import { menuPageUrl } from '../config'

defineProps<{
  title: string
  showBack?: boolean
}>()

function goMenu(): void {
  window.location.href = menuPageUrl
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <button
        v-if="showBack !== false"
        type="button"
        class="btn-back"
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
