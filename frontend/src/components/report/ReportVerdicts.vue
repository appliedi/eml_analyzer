<script setup lang="ts">
import { type PropType } from 'vue'

import { verdictStyle } from '@/composables/useVerdictScoring'
import type { VerdictType } from '@/schemas'

defineProps({
  verdicts: {
    type: Array as PropType<VerdictType[]>,
    required: true
  }
})
</script>

<template>
  <div class="grid gap-4">
    <div
      v-for="verdict in verdicts"
      :key="verdict.name"
      class="report-verdict-card border-l-4 rounded p-4"
      :class="verdictStyle(verdict).border"
    >
      <h3 class="font-bold text-base flex items-center gap-2">
        <font-awesome-icon
          :icon="verdictStyle(verdict).icon"
          class="w-4 h-4"
          :class="verdictStyle(verdict).color"
        />
        {{ verdict.name }}
        <span v-if="verdict.score != null" class="font-normal text-sm">
          ({{ verdict.score.toFixed(2) }})
        </span>
      </h3>
      <ul class="mt-2 list-disc list-inside text-sm" v-if="verdict.details.length > 0">
        <li v-for="detail in verdict.details" :key="detail.key">
          {{ detail.description }}
          <span v-if="detail.score != null" class="text-base-content/60">
            &mdash; score: {{ detail.score.toFixed(2) }}
          </span>
          <span v-if="detail.referenceLink" class="text-base-content/60">
            ({{ detail.referenceLink }})
          </span>
        </li>
      </ul>
      <p class="mt-2 text-sm text-base-content/60" v-else>No details available</p>
    </div>
  </div>
</template>
