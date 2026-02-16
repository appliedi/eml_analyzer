<script setup lang="ts">
import { type PropType, toRef } from 'vue'

import { useVerdictScoring } from '@/composables/useVerdictScoring'
import type { VerdictType } from '@/schemas'

const props = defineProps({
  verdicts: {
    type: Array as PropType<VerdictType[]>,
    required: true
  }
})

const { safetyPercentage, safeCount, totalCount, riskLabel, riskColor, borderColor, riskIcon } =
  useVerdictScoring(toRef(props, 'verdicts'))
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
        <h2 class="text-2xl font-bold flex items-center gap-2" :class="riskColor">
          <font-awesome-icon v-if="riskIcon" :icon="riskIcon" class="w-6 h-6" />
          {{ riskLabel }}
        </h2>
        <p class="text-base-content/60" v-if="totalCount > 0">
          {{ safeCount }}/{{ totalCount }} services report clean
        </p>
        <p class="text-base-content/60" v-else>No verdict services ran</p>
      </div>
    </div>
  </div>
</template>
