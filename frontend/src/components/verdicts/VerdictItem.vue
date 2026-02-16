<script setup lang="ts">
import { computed, type PropType } from 'vue'

import Detail from '@/components/verdicts/DetailItem.vue'
import { verdictStyle } from '@/composables/useVerdictScoring'
import type { DetailType, VerdictType } from '@/schemas'

const props = defineProps({
  verdict: {
    type: Object as PropType<VerdictType>,
    required: true
  }
})

const title = computed(() => {
  return `${props.verdict.name}`
})

const score = computed(() => {
  return props.verdict.score ? props.verdict.score.toFixed(2) : 'N/A'
})

const style = computed(() => verdictStyle(props.verdict))

const details = computed((): DetailType[] => {
  if (props.verdict.details.length > 0) {
    return props.verdict.details
  }
  return [{ key: 'N/A', description: 'No details available', score: null }]
})
</script>

<template>
  <div class="card border-1" :class="style.border">
    <div class="card-body">
      <h3 class="card-title text-base">
        <font-awesome-icon :icon="style.icon" class="w-4 h-4" :class="style.color" />
        {{ title }}
        <div v-if="verdict.score != null" class="badge">{{ score }}</div>
      </h3>
      <ul class="list">
        <Detail v-for="detail in details" :detail="detail" :key="detail.key" />
      </ul>
    </div>
  </div>
</template>
