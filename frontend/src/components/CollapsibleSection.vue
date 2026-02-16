<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(
  defineProps<{
    id: string
    title: string
    icon: string
    defaultOpen?: boolean
    count?: number
  }>(),
  {
    defaultOpen: false
  }
)

const isOpen = ref(props.defaultOpen)
</script>

<template>
  <div :id="id" class="collapse collapse-arrow border border-base-300 bg-base-100">
    <input type="checkbox" v-model="isOpen" />
    <div class="collapse-title font-semibold text-lg flex items-center gap-2">
      <font-awesome-icon :icon="icon" class="w-4 h-4" />
      <span>{{ title }}</span>
      <span v-if="count !== undefined" class="badge badge-sm">{{ count }}</span>
    </div>
    <div class="collapse-content">
      <slot />
    </div>
  </div>
</template>
