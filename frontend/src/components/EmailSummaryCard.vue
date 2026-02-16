<script setup lang="ts">
import { type PropType } from 'vue'

import IndicatorButton from '@/components/IndicatorButton.vue'
import type { HeaderType } from '@/schemas'
import { toUTC } from '@/utils'

defineProps({
  header: {
    type: Object as PropType<HeaderType>,
    required: true
  }
})
</script>

<template>
  <div class="card border border-base-300 bg-base-100">
    <div class="card-body">
      <h3 class="card-title text-lg">
        <font-awesome-icon icon="envelope" class="w-4 h-4" />
        {{ header.subject }}
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
        <div v-if="header.from">
          <span class="text-xs font-semibold uppercase text-base-content/50">From</span>
          <div>
            <IndicatorButton :value="header.from" />
          </div>
        </div>
        <div v-if="header.to.length > 0">
          <span class="text-xs font-semibold uppercase text-base-content/50">To</span>
          <div class="flex flex-wrap gap-1">
            <IndicatorButton :value="email" v-for="email in header.to" :key="email" />
          </div>
        </div>
        <div>
          <span class="text-xs font-semibold uppercase text-base-content/50">Date</span>
          <div>{{ toUTC(header.date) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
