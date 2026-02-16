<script setup lang="ts">
import { computed, type PropType } from 'vue'

import type { EmlType } from '@/schemas'

const props = defineProps({
  eml: {
    type: Object as PropType<EmlType>,
    required: true
  }
})

const urlCount = computed(() => {
  const urls = new Set<string>()
  for (const body of props.eml.bodies) {
    for (const url of body.urls) urls.add(url)
  }
  return urls.size
})

const domainCount = computed(() => {
  const domains = new Set<string>()
  for (const body of props.eml.bodies) {
    for (const domain of body.domains) domains.add(domain)
  }
  return domains.size
})

const ipCount = computed(() => {
  const ips = new Set<string>()
  for (const body of props.eml.bodies) {
    for (const ip of body.ipAddresses) ips.add(ip)
  }
  return ips.size
})

const attachmentCount = computed(() => props.eml.attachments.length)

const hopCount = computed(() => props.eml.header.received?.length ?? 0)
</script>

<template>
  <div class="stats stats-vertical lg:stats-horizontal shadow w-full">
    <div class="stat">
      <div class="stat-figure text-primary">
        <font-awesome-icon icon="link" class="w-5 h-5" />
      </div>
      <div class="stat-title">URLs</div>
      <div class="stat-value text-lg">{{ urlCount }}</div>
    </div>
    <div class="stat">
      <div class="stat-figure text-primary">
        <font-awesome-icon icon="globe" class="w-5 h-5" />
      </div>
      <div class="stat-title">Domains</div>
      <div class="stat-value text-lg">{{ domainCount }}</div>
    </div>
    <div class="stat">
      <div class="stat-figure text-primary">
        <font-awesome-icon icon="network-wired" class="w-5 h-5" />
      </div>
      <div class="stat-title">IPs</div>
      <div class="stat-value text-lg">{{ ipCount }}</div>
    </div>
    <div class="stat">
      <div class="stat-figure text-primary">
        <font-awesome-icon icon="paperclip" class="w-5 h-5" />
      </div>
      <div class="stat-title">Attachments</div>
      <div class="stat-value text-lg">{{ attachmentCount }}</div>
    </div>
    <div class="stat">
      <div class="stat-figure text-primary">
        <font-awesome-icon icon="route" class="w-5 h-5" />
      </div>
      <div class="stat-title">Hops</div>
      <div class="stat-value text-lg">{{ hopCount }}</div>
    </div>
  </div>
</template>
