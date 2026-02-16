<script setup lang="ts">
import { computed, type PropType, toRef } from 'vue'

import IndicatorButton from '@/components/IndicatorButton.vue'
import IOCStatusCell from '@/components/ioc-table/IOCStatusCell.vue'
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

const typeBadgeClass: Record<IOCType, string> = {
  url: 'badge-primary',
  domain: 'badge-secondary',
  ip: 'badge-accent',
  email: 'badge-info',
  sha256: 'badge-neutral'
}

const hasRows = computed(() => rows.value.length > 0)
</script>

<template>
  <div v-if="hasRows" class="overflow-x-auto">
    <table class="table table-xs w-full">
      <thead>
        <tr>
          <th>IOC</th>
          <th>Type</th>
          <th v-for="col in columns" :key="col.name" class="text-center">
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.ioc" :class="{ 'bg-error/5': row.isMalicious }">
          <td>
            <IndicatorButton :value="row.ioc" />
          </td>
          <td>
            <span class="badge badge-sm" :class="typeBadgeClass[row.type]">
              {{ row.type }}
            </span>
          </td>
          <IOCStatusCell
            v-for="col in columns"
            :key="col.name"
            :service-result="row.services.get(col.name)!"
          />
        </tr>
      </tbody>
    </table>
  </div>
</template>
