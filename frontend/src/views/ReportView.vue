<script setup lang="ts">
import Report from '@/components/report/ReportItem.vue'

defineProps({
  id: {
    type: String,
    required: true
  }
})
</script>

<template>
  <Report :id="id" />
</template>
