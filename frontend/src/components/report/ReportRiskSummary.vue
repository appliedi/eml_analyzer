<script setup lang="ts">
import { computed, type PropType } from 'vue'

import type { ResponseType } from '@/schemas'

const props = defineProps({
  response: {
    type: Object as PropType<ResponseType>,
    required: true
  }
})

const maliciousCount = computed(() => props.response.verdicts.filter((v) => v.malicious).length)
const totalCount = computed(() => props.response.verdicts.length)
const safeCount = computed(() => totalCount.value - maliciousCount.value)
const safetyPercentage = computed(() => {
  if (totalCount.value === 0) return 100
  return Math.round((safeCount.value / totalCount.value) * 100)
})

const riskLevel = computed(() => {
  if (totalCount.value === 0) return 'unknown'
  if (maliciousCount.value === 0) return 'clean'
  if (maliciousCount.value >= totalCount.value / 2) return 'malicious'
  return 'suspicious'
})

const riskLabel = computed(() => {
  const labels: Record<string, string> = {
    unknown: 'No Verdicts',
    clean: 'Clean',
    suspicious: 'Suspicious',
    malicious: 'Malicious'
  }
  return labels[riskLevel.value]
})

const riskColor = computed(() => {
  const colors: Record<string, string> = {
    unknown: 'text-base-content',
    clean: 'text-success',
    suspicious: 'text-warning',
    malicious: 'text-error'
  }
  return colors[riskLevel.value]
})

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
      <span class="text-2xl font-bold ml-2" :class="riskColor">&mdash; {{ riskLabel }}</span>
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
        :class="verdict.malicious ? 'border-error text-error' : 'border-success text-success'"
      >
        <font-awesome-icon
          :icon="verdict.malicious ? 'triangle-exclamation' : 'circle-check'"
          class="w-3 h-3"
        />
        {{ verdict.name }}
        <span class="font-medium ml-1">{{
          verdict.score != null ? verdict.score.toFixed(2) : 'N/A'
        }}</span>
      </span>
    </div>
  </div>
</template>
