<script setup lang="ts">
import { type PropType } from 'vue'

import OverallRiskIndicator from '@/components/scorecard/OverallRiskIndicator.vue'
import QuickStats from '@/components/scorecard/QuickStats.vue'
import VerdictSummaryGrid from '@/components/scorecard/VerdictSummaryGrid.vue'
import type { ResponseType } from '@/schemas'

defineProps({
  response: {
    type: Object as PropType<ResponseType>,
    required: true
  }
})
</script>

<template>
  <div class="grid gap-4">
    <OverallRiskIndicator :verdicts="response.verdicts" />
    <QuickStats :eml="response.eml" />
    <VerdictSummaryGrid :verdicts="response.verdicts" />
  </div>
</template>
