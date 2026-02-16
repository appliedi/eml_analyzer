<script setup lang="ts">
import { computed, type PropType } from 'vue'

import { basicKeys, securityKeys } from '@/constants'
import type { HeaderItemType, HeaderType } from '@/schemas'
import { humanizeSeconds, toCSV, toUTC } from '@/utils'

interface ReceivedWithIndex {
  index: number
  received: {
    by?: string[] | null
    date: string
    from?: string[] | null
    with?: string | null
    delay?: number | null
  }
}

const props = defineProps({
  header: {
    type: Object as PropType<HeaderType>,
    required: true
  }
})

const receivedWithIndexes = computed(() => {
  const received = props.header.received || []
  return received.map((received_, index): ReceivedWithIndex => {
    return { index: index + 1, received: received_ }
  })
})

const securityHeaders = computed(() => {
  const header = props.header.header
  const items = securityKeys.map((key) => {
    if (key in header) {
      return { key: key, values: header[key] }
    }
  })
  return items.filter((x): x is HeaderItemType => x !== undefined)
})

const xHeaders = computed(() => {
  const header = props.header.header
  const keys = Object.keys(header)
  const xKeys = keys.filter((key) => key.startsWith('x-'))
  const items = xKeys.map((key) => {
    if (key in header) {
      return { key: key, values: header[key] }
    }
  })
  return items.filter((x): x is HeaderItemType => x !== undefined)
})

const otherHeaders = computed(() => {
  const header = props.header.header
  const keys = Object.keys(header)
  const otherKeys = keys
    .filter((key) => !key.startsWith('x-'))
    .filter((key) => securityKeys.indexOf(key) == -1)
    .filter((key) => basicKeys.indexOf(key) == -1)
  const items = otherKeys.map((key) => {
    if (key in header) {
      return { key: key, values: header[key] }
    }
  })
  return items.filter((x): x is HeaderItemType => x !== undefined)
})

interface FlattenHeader {
  id: string
  key: string
  value: string | number
}

function flatten(headers: HeaderItemType[]): FlattenHeader[] {
  const result: FlattenHeader[] = []
  let index = 0
  for (const header of headers) {
    for (const value of header.values) {
      index += 1
      result.push({ id: header.key + index.toString(), key: header.key, value })
    }
  }
  return result
}
</script>

<template>
  <div class="grid gap-6">
    <div v-if="receivedWithIndexes.length > 0">
      <h3 class="text-lg font-bold mb-2">Hops</h3>
      <table class="table w-full break-all">
        <thead>
          <tr>
            <th>Hop</th>
            <th>From</th>
            <th>By</th>
            <th>With</th>
            <th>Date (UTC)</th>
            <th>Delay</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hop in receivedWithIndexes" :key="hop.index">
            <td>{{ hop.index }}</td>
            <td>{{ toCSV(hop.received.from || []) }}</td>
            <td>{{ toCSV(hop.received.by || []) }}</td>
            <td>{{ hop.received.with }}</td>
            <td>{{ toUTC(hop.received.date) }}</td>
            <td>{{ hop.received.delay ? humanizeSeconds(hop.received.delay) : 'N/A' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div>
      <h3 class="text-lg font-bold mb-2">Basic headers</h3>
      <table class="table w-full break-all">
        <tbody>
          <tr>
            <th class="w-48">Message ID</th>
            <td>{{ header.messageId || 'N/A' }}</td>
          </tr>
          <tr>
            <th class="w-48">Subject</th>
            <td>{{ header.subject }}</td>
          </tr>
          <tr>
            <th class="w-48">Date (UTC)</th>
            <td>{{ toUTC(header.date) }}</td>
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
            <th class="w-48">Cc</th>
            <td>{{ (header.cc || []).join(', ') }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="securityHeaders.length > 0">
      <h3 class="text-lg font-bold mb-2">Security headers</h3>
      <table class="table w-full break-all">
        <tbody>
          <tr v-for="h in flatten(securityHeaders)" :key="h.id">
            <th class="w-48">{{ h.key }}</th>
            <td>{{ h.value }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="xHeaders.length > 0">
      <h3 class="text-lg font-bold mb-2">X headers</h3>
      <table class="table w-full break-all">
        <tbody>
          <tr v-for="h in flatten(xHeaders)" :key="h.id">
            <th class="w-48">{{ h.key }}</th>
            <td>{{ h.value }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="otherHeaders.length > 0">
      <h3 class="text-lg font-bold mb-2">Other headers</h3>
      <table class="table w-full break-all">
        <tbody>
          <tr v-for="h in flatten(otherHeaders)" :key="h.id">
            <th class="w-48">{{ h.key }}</th>
            <td>{{ h.value }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
