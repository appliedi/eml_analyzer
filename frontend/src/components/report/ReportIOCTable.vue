<script setup lang="ts">
import truncate from 'just-truncate'
import { type PropType, toRef } from 'vue'

import { type IOCType, useIOCTable } from '@/composables/useIOCTable'
import { useStatus } from '@/composables/useStatus'
import type { ResponseType } from '@/schemas'

const props = defineProps({
  response: {
    type: Object as PropType<ResponseType>,
    required: true
  }
})

const { status } = useStatus()
const { rows, columns } = useIOCTable(toRef(props, 'response'), status)

const typeLabels: Record<IOCType, string> = {
  url: 'URL',
  domain: 'Domain',
  ip: 'IP',
  email: 'Email',
  sha256: 'SHA256'
}
</script>

<template>
  <div v-if="rows.length > 0">
    <table class="w-full break-all text-sm">
      <thead>
        <tr>
          <th class="text-left">IOC</th>
          <th class="text-left">Type</th>
          <th v-for="col in columns" :key="col.name" class="text-center">
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.ioc">
          <td class="font-mono text-xs">{{ truncate(row.ioc, 80) }}</td>
          <td>{{ typeLabels[row.type] }}</td>
          <td v-for="col in columns" :key="col.name" class="text-center">
            <template v-if="row.services.get(col.name)!.state === 'na'">
              <font-awesome-icon icon="minus" class="w-3 h-3 text-base-content/30" />
            </template>
            <template v-else-if="row.services.get(col.name)!.state === 'errored'">
              <font-awesome-icon icon="minus" class="w-3 h-3 text-warning" />
            </template>
            <template v-else-if="row.services.get(col.name)!.state === 'flagged'">
              <font-awesome-icon icon="triangle-exclamation" class="w-3 h-3 text-error" />
            </template>
            <template v-else>
              <font-awesome-icon icon="circle-check" class="w-3 h-3 text-success" />
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
