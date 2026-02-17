<script setup lang="ts">
import type { IOCServiceResult } from '@/composables/useIOCTable'

defineProps<{
  serviceResult: IOCServiceResult
}>()
</script>

<template>
  <td class="text-center">
    <!-- Not applicable: service doesn't cover this IOC type -->
    <font-awesome-icon
      v-if="serviceResult.state === 'na'"
      icon="minus"
      class="w-4 h-4 text-base-content/30"
    />
    <!-- Errored: service was expected to run but returned no verdict -->
    <span v-else-if="serviceResult.state === 'errored'" class="tooltip" :data-tip="serviceResult.errorMessage || 'Service unavailable (error or quota)'">
      <font-awesome-icon icon="minus" class="w-4 h-4 text-warning" />
    </span>
    <!-- Flagged: service found this IOC in its details -->
    <span
      v-else-if="serviceResult.state === 'flagged'"
      class="tooltip"
      :data-tip="
        serviceResult.detail
          ? serviceResult.detail.description +
            (serviceResult.detail.score != null
              ? ` (score: ${serviceResult.detail.score.toFixed(2)})`
              : '')
          : 'Flagged'
      "
    >
      <a
        v-if="serviceResult.detail?.referenceLink"
        :href="serviceResult.detail.referenceLink"
        target="_blank"
        class="inline-flex"
      >
        <font-awesome-icon icon="triangle-exclamation" class="w-4 h-4 text-error" />
      </a>
      <font-awesome-icon v-else icon="triangle-exclamation" class="w-4 h-4 text-error" />
    </span>
    <!-- Clean: service ran and IOC not in its flagged details -->
    <font-awesome-icon v-else icon="circle-check" class="w-4 h-4 text-success" />
  </td>
</template>
