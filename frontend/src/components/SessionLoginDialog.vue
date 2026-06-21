<script setup lang="ts">
import { sessionLoginDialog, cancelSessionLogin, submitSessionLogin } from '../api/sessionAuth'
</script>

<template>
  <div
    v-if="sessionLoginDialog.open"
    class="modal-overlay"
    role="dialog"
    aria-modal="true"
    aria-labelledby="session-login-title"
  >
    <form class="modal-card" @submit.prevent="submitSessionLogin">
      <h2 id="session-login-title">ログイン</h2>
      <p class="hint">セッションの有効期限が切れました。再ログインしてください。</p>
      <label>
        ユーザー名
        <input
          v-model="sessionLoginDialog.username"
          type="text"
          autocomplete="username"
          :disabled="sessionLoginDialog.loading"
        />
      </label>
      <label>
        パスワード
        <input
          v-model="sessionLoginDialog.password"
          type="password"
          autocomplete="current-password"
          :disabled="sessionLoginDialog.loading"
        />
      </label>
      <p v-if="sessionLoginDialog.error" class="error">{{ sessionLoginDialog.error }}</p>
      <div class="actions">
        <button type="button" :disabled="sessionLoginDialog.loading" @click="cancelSessionLogin">
          キャンセル
        </button>
        <button type="submit" class="primary" :disabled="sessionLoginDialog.loading">
          {{ sessionLoginDialog.loading ? 'ログイン中…' : 'ログイン' }}
        </button>
      </div>
    </form>
  </div>
</template>
