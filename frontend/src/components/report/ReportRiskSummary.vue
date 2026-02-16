<script setup lang="ts">
import { computed, type PropType, toRef } from 'vue'

import { useVerdictScoring, verdictStyle } from '@/composables/useVerdictScoring'
import type { ResponseType } from '@/schemas'

const props = defineProps({
  response: {
    type: Object as PropType<ResponseType>,
    required: true
  }
})

const { safetyPercentage, safeCount, totalCount, riskLabel, riskColor, riskIcon } =
  useVerdictScoring(toRef(() => props.response.verdicts))

const urlCount = computed(() => {
  const urls = new Set<string>()
  for (const body of props.response.eml.bodies) {
    for (const url of body.urls) urls.add(url)
  }
  return urls.size
})

const domainCount = computed(() => {
  const domains = new Set<string>()
  for (const body of props.response.eml.bodies) {
    for (const domain of body.domains) domains.add(domain)
  }
  return domains.size
})

const ipCount = computed(() => {
  const ips = new Set<string>()
  for (const body of props.response.eml.bodies) {
    for (const ip of body.ipAddresses) ips.add(ip)
  }
  return ips.size
})

const attachmentCount = computed(() => props.response.eml.attachments.length)
const hopCount = computed(() => props.response.eml.header.received?.length ?? 0)
</script>

<template>
  <div>
    <div class="mb-4">
      <span class="text-3xl font-bold" :class="riskColor">{{ safetyPercentage }}%</span>
      <span class="text-2xl font-bold ml-2" :class="riskColor">
        <font-awesome-icon v-if="riskIcon" :icon="riskIcon" class="w-5 h-5" />
        &mdash; {{ riskLabel }}
      </span>
      <p class="text-base-content/60 mt-1" v-if="totalCount > 0">
        {{ safeCount }}/{{ totalCount }} services report clean
      </p>
      <p class="text-base-content/60 mt-1" v-else>No verdict services ran</p>
    </div>

    <table class="table w-full">
      <thead>
        <tr>
          <th>URLs</th>
          <th>Domains</th>
          <th>IPs</th>
          <th>Attachments</th>
          <th>Hops</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{{ urlCount }}</td>
          <td>{{ domainCount }}</td>
          <td>{{ ipCount }}</td>
          <td>{{ attachmentCount }}</td>
          <td>{{ hopCount }}</td>
        </tr>
      </tbody>
    </table>

    <div class="flex flex-wrap gap-2 mt-4" v-if="response.verdicts.length > 0">
      <span
        v-for="verdict in response.verdicts"
        :key="verdict.name"
        class="inline-flex items-center gap-1 rounded border px-2 py-1 text-sm"
        :class="[verdictStyle(verdict).border, verdictStyle(verdict).color]"
      >
        <font-awesome-icon :icon="verdictStyle(verdict).icon" class="w-3 h-3" />
        {{ verdict.name }}
        <span class="font-medium ml-1">{{
          verdict.score != null ? verdict.score.toFixed(2) : 'N/A'
        }}</span>
      </span>
    </div>
  </div>
</template>
