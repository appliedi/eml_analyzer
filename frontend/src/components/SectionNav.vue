<script setup lang="ts">
defineProps<{
  sections: { id: string; label: string; icon: string; count?: number }[]
}>()

const scrollTo = (id: string) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <div class="sticky top-0 z-10 bg-base-100/95 backdrop-blur py-2">
    <div role="tablist" class="tabs tabs-box">
      <a
        v-for="section in sections"
        :key="section.id"
        role="tab"
        class="tab gap-2"
        @click="scrollTo(section.id)"
      >
        <font-awesome-icon :icon="section.icon" class="w-4 h-4" />
        <span>{{ section.label }}</span>
        <span v-if="section.count !== undefined" class="badge badge-sm">{{ section.count }}</span>
      </a>
    </div>
  </div>
</template>
