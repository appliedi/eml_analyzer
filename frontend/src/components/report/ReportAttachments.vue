<script setup lang="ts">
import fileSize from 'filesize.js'
import { type PropType } from 'vue'

import type { AttachmentType } from '@/schemas'

defineProps({
  attachments: {
    type: Array as PropType<AttachmentType[]>,
    required: true
  }
})
</script>

<template>
  <div class="grid gap-4">
    <div
      v-for="attachment in attachments"
      :key="attachment.hash.md5"
      class="report-attachment-card"
    >
      <h3 class="text-base font-bold mb-2">{{ attachment.filename }}</h3>
      <table class="table w-full break-all">
        <tbody>
          <tr>
            <th class="w-48">Filename</th>
            <td>{{ attachment.filename }}</td>
          </tr>
          <tr>
            <th class="w-48">Size</th>
            <td>{{ fileSize(attachment.size) }}</td>
          </tr>
          <tr>
            <th class="w-48">MIME type</th>
            <td>{{ attachment.mimeType || 'N/A' }}</td>
          </tr>
          <tr>
            <th class="w-48">CID</th>
            <td>{{ attachment.contentId || 'N/A' }}</td>
          </tr>
          <tr>
            <th class="w-48">SHA256</th>
            <td>{{ attachment.hash.sha256 }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
