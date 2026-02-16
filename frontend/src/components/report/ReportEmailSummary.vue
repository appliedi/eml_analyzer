<script setup lang="ts">
import { type PropType } from 'vue'

import type { HeaderType } from '@/schemas'
import { toUTC } from '@/utils'

defineProps({
  header: {
    type: Object as PropType<HeaderType>,
    required: true
  }
})
</script>

<template>
  <table class="table w-full break-all">
    <tbody>
      <tr>
        <th class="w-48">Subject</th>
        <td>{{ header.subject }}</td>
      </tr>
      <tr v-if="header.from">
        <th class="w-48">From</th>
        <td>{{ header.from }}</td>
      </tr>
      <tr v-if="header.to.length > 0">
        <th class="w-48">To</th>
        <td>{{ header.to.join(', ') }}</td>
      </tr>
      <tr v-if="(header.cc || []).length > 0">
        <th class="w-48">CC</th>
        <td>{{ (header.cc || []).join(', ') }}</td>
      </tr>
      <tr>
        <th class="w-48">Date (UTC)</th>
        <td>{{ toUTC(header.date) }}</td>
      </tr>
      <tr>
        <th class="w-48">Message-ID</th>
        <td>{{ header.messageId || 'N/A' }}</td>
      </tr>
    </tbody>
  </table>
</template>
