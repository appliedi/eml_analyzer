<script setup lang="ts">
import { computed, type PropType } from 'vue'

import type { VerdictType } from '@/schemas'

const props = defineProps({
  verdicts: {
    type: Array as PropType<VerdictType[]>,
    required: true
  }
})

const maliciousCount = computed(() => props.verdicts.filter((v) => v.malicious).length)
const totalCount = computed(() => props.verdicts.length)
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

const borderColor = computed(() => {
  const colors: Record<string, string> = {
    unknown: 'border-base-300',
    clean: 'border-success',
    suspicious: 'border-warning',
    malicious: 'border-error'
  }
  return colors[riskLevel.value]
})
</script>

<template>
  <div class="card border-l-4 bg-base-100" :class="borderColor">
    <div class="card-body flex-row items-center gap-6">
      <div
        class="radial-progress"
        :class="riskColor"
        :style="`--value: ${safetyPercentage}; --size: 8rem; --thickness: 0.5rem;`"
        role="progressbar"
      >
        <span class="text-2xl font-bold">{{ safetyPercentage }}%</span>
      </div>
      <div>
        <h2 class="text-2xl font-bold" :class="riskColor">{{ riskLabel }}</h2>
        <p class="text-base-content/60" v-if="totalCount > 0">
          {{ safeCount }}/{{ totalCount }} services report clean
        </p>
        <p class="text-base-content/60" v-else>No verdict services ran</p>
      </div>
    </div>
  </div>
</template>
