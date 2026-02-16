<script setup lang="ts">
import { type PropType } from 'vue'

import type { BodyType } from '@/schemas'

defineProps({
  bodies: {
    type: Array as PropType<BodyType[]>,
    required: true
  }
})
</script>

<template>
  <div class="grid gap-6">
    <div v-for="(body, index) in bodies" :key="body.hash">
      <h3 class="text-lg font-bold mb-2">
        Body {{ index + 1 }}: {{ body.contentType || 'unknown' }}
      </h3>
      <details class="mt-1 mb-2">
        <summary class="cursor-pointer text-sm font-medium text-base-content/70">
          Show body content
        </summary>
        <pre class="whitespace-pre-wrap break-all bg-base-200 p-4 rounded text-sm mt-2">{{
          body.content
        }}</pre>
      </details>

      <table class="table w-full break-all mt-2" v-if="body.urls.length > 0">
        <thead>
          <tr>
            <th>Extracted URLs</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="url in body.urls" :key="url">
            <td>{{ url }}</td>
          </tr>
        </tbody>
      </table>

      <table class="table w-full break-all mt-2" v-if="body.emails.length > 0">
        <thead>
          <tr>
            <th>Extracted emails</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="email in body.emails" :key="email">
            <td>{{ email }}</td>
          </tr>
        </tbody>
      </table>

      <table class="table w-full break-all mt-2" v-if="body.domains.length > 0">
        <thead>
          <tr>
            <th>Extracted domains</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="domain in body.domains" :key="domain">
            <td>{{ domain }}</td>
          </tr>
        </tbody>
      </table>

      <table class="table w-full break-all mt-2" v-if="body.ipAddresses.length > 0">
        <thead>
          <tr>
            <th>Extracted IPs</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ip in body.ipAddresses" :key="ip">
            <td>{{ ip }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
