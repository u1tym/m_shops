<script setup lang="ts">
import { RouterView } from 'vue-router'

import SessionLoginDialog from './components/SessionLoginDialog.vue'
</script>

<template>
  <div class="app-shell">
    <RouterView />
    <SessionLoginDialog />
  </div>
</template>
