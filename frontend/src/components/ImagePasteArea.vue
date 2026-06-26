<script setup lang="ts">
import type { FormImageItem } from '../api/types'
import { fileToDataUrl, newKey } from '../utils/helpers'

const images = defineModel<FormImageItem[]>({ required: true })

const MAX_BYTES = 5_242_880

async function addFromFile(file: File): Promise<void> {
  if (!file.type.startsWith('image/')) {
    window.alert('画像ファイルを貼り付けてください')
    return
  }
  if (file.size > MAX_BYTES) {
    window.alert('画像サイズは 5MB 以下にしてください')
    return
  }
  const dataUrl = await fileToDataUrl(file)
  images.value = [
    ...images.value,
    {
      key: newKey(),
      file_name: file.name || null,
      mime_type: file.type,
      previewUrl: dataUrl,
      data_base64: dataUrl,
      sort_order: images.value.length,
    },
  ]
}

async function onPaste(event: ClipboardEvent): Promise<void> {
  const items = event.clipboardData?.items
  if (!items) {
    return
  }
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      event.preventDefault()
      const file = item.getAsFile()
      if (file) {
        await addFromFile(file)
      }
      return
    }
  }
}

function removeImage(key: string): void {
  const target = images.value.find((img) => img.key === key)
  if (target?.previewUrl.startsWith('blob:')) {
    URL.revokeObjectURL(target.previewUrl)
  }
  images.value = images.value
    .filter((img) => img.key !== key)
    .map((img, index) => ({ ...img, sort_order: index }))
}
</script>

<template>
  <section class="image-paste">
    <h3>参考画像</h3>
    <p class="hint">下の枠をクリックして Ctrl+V（貼り付け）で画像を追加できます。</p>
    <div
      class="paste-zone"
      tabindex="0"
      @paste="onPaste"
    >
      ここに画像を貼り付け
    </div>
    <div v-if="images.length" class="image-grid detail-images">
      <figure v-for="img in images" :key="img.key" class="image-item">
        <img :src="img.previewUrl" :alt="img.file_name ?? '参考画像'" />
        <figcaption>{{ img.file_name ?? '画像' }}</figcaption>
        <button type="button" class="btn small danger" @click="removeImage(img.key)">削除</button>
      </figure>
    </div>
  </section>
</template>
