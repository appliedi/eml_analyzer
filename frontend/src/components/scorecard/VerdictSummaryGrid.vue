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
  <div class="flex flex-wrap gap-2" v-if="verdicts.length > 0">
    <div
      v-for="verdict in verdicts"
      :key="verdict.name"
      class="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm"
      :class="[verdictStyle(verdict).border, verdictStyle(verdict).bg, verdictStyle(verdict).color]"
    >
      <font-awesome-icon :icon="verdictStyle(verdict).icon" class="w-4 h-4" />
      <span class="font-medium">{{ verdict.name }}</span>
      <span class="badge badge-sm" :class="verdictStyle(verdict).badge">
        {{ verdict.score ? verdict.score.toFixed(2) : 'N/A' }}
      </span>
    </div>
  </div>
</template>
